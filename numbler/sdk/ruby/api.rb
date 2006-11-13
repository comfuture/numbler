# Copyright (c) 2006 Jin Choi
# see LICENSE for details

require 'uri'
require 'base64'
require 'openssl'
require 'rexml/document'

module Numbler
  def translate_col(col)
    if !col.is_a? Integer
      return col
    end
    v = col - 1
    if v < 26
      return "%c" % (v + 97)
    else
      a = v / 26 - 1
      return "%c%c" % [a + 97, v % 26 + 97]
    end
  end

  class Connection
    include Numbler
    DEFAULT_OPTIONS = {
      :host => 'ws.numbler.com',
      :port => 80,
      :secure? => false
    }.freeze

    def initialize(sheetUID, api_id, secret_key, options={})
      @api_id = api_id
      @secret_key = secret_key
      @sheetUID = sheetUID
      @options = DEFAULT_OPTIONS.merge(options)
      if @options[:secure?]
        require 'net/https'
        if @options[:port] == 80
          @options[:port] = 443
        end
        @con = Net::HTTP.new(@options[:host], @options[:port])
        @con.use_ssl = true
      else
        require 'net/http'
        @con = Net::HTTP.new(@options[:host], @options[:port])
      end
    end

    
    def get_cell(col, row)
      request Net::HTTP::Get.new(cell(col, row))
    end

    def get_cell_range(startcol, startrow, endcol, endrow)
      request Net::HTTP::Get.new(cell_range(startcol, startrow, endcol, endrow))
    end

    def get_row_range(startrow, endrow)
      request Net::HTTP::Get.new(row_range(startrow, endrow))
    end

    def get_col_range(startcol, endcol)
      request Net::HTTP::Get.new(col_range(startcol, endcol))
    end

    def delete_cell(col, row, get_results=true)
      args = get_results ? {} : {'recvResults' => 0}
      request Net::HTTP::Delete.new(cell(col, row, args))
    end

    def delete_cell_range(startcol, startrow, endcol, endrow, get_results=true)
      args = get_results ? {} : {'recvResults' => 0}
      request Net::HTTP::Delete.new(cell_range(startcol, startrow, endcol, endrow, args))
    end

    def delete_row_range(startrow, endrow, get_results=true)
      args = get_results ? {} : {'recvResults' => 0}
      request Net::HTTP::Delete.new(row_range(startrow, endrow, args))
    end

    def delete_col_range(startcol, endcol, get_results=true)
      args = get_results ? {} : {'recvResults' => 0}
      request Net::HTTP::Delete.new(col_range(startcol, endcol, args))
    end

    def get_all_cells
      request Net::HTTP::Get.new("/#{@sheetUID}/API")
    end

    def new_cell_updater
      Numbler::RequestGenerator.new(@sheetUID)
    end

    def send_cells(gen, get_changed_cells=true)
      args = get_changed_cells ? {} : {'recvResults' => 0}
      request Net::HTTP::Put.new("/#{@sheetUID}/API#{hash_to_url_params(args)}"), gen.to_xml
    end

    def put_cell(col, row, formula, get_changed_cells=true)
      gen = new_cell_updater
      gen.add_cell(col, row, formula)
      send_cells(gen, get_changed_cells)
    end

    private
    def request(req, body=nil)
      add_auth_headers req
      @con.request req, body
    end
    
    def auth_hash(req)
      encodestr = [req.method, "\n", 
        req['content-md5'], "\n",
        req['content-type'], "\n",
        req['x-numbler-date'], "\n",
        req.path].join
      Base64.encode64(OpenSSL::HMAC.digest(OpenSSL::Digest::Digest.new('sha1'), @secret_key, encodestr)).strip
    end
    
    def add_auth_headers(req)
      req['content-type'] = 'text/xml'
      req['x-numbler-date'] = Time.now.gmtime.strftime('%a, %d %b %Y %X GMT')
      req['Authorization'] = "NUMBLER #{@api_id}:#{auth_hash(req)}"
    end

    def hash_to_url_params(args)
      params = []
      args.each do |key, value|
        params << "#{URI.escape(key)}=#{URI.escape(value.to_s)}"
      end
      params.empty? ? '' : '?' + params.join('&')
    end
    
    def cell(col, row, args={})
      col = translate_col col
      "/#{@sheetUID}/API/#{col}#{row}#{hash_to_url_params(args)}"
    end

    def cell_range(startcol, startrow, endcol, endrow, args={})
      startcol = translate_col startcol
      endcol = translate_col endcol
      "/#{@sheetUID}/API/#{startcol}#{startrow}-#{endcol}#{endrow}#{hash_to_url_params(args)}"
    end

    def row_range(startrow, endrow, args={})
      "/#{@sheetUID}/API/#{startrow}-#{endrow}#{hash_to_url_params(args)}"
    end
    
    def col_range(startcol, endcol, args={})
      startcol = translate_col startcol
      endcol = translate_col endcol
      "/#{@sheetUID}/API/#{startcol}-#{endcol}#{hash_to_url_params(args)}"
    end
  end

  class RequestGenerator
    include Numbler
    def initialize(sheetUID)
      @cells = []
      @sheetUID = sheetUID
    end
    
    def add_cell(col, row, formula)
      col = translate_col col
      @cells << [col, row.to_s, formula.to_s]
    end

    def to_xml
      d = REXML::Document.new
      d << REXML::XMLDecl.new('1.0', 'UTF-8')
      d.add_element 'xml'
      d.root.add_element 'sheet', {'guid' => @sheetUID}
      @cells.each do |c|
        col, row, f = c
        d.root[0].add_element 'cell', {'row' => row, 'col' => col, 'formula' => f}
      end
      d.to_s
    end
  end

  # A simple parser to make XML returned in responses available as hashes.
  class Response
    def initialize(xmlstr)
      @doc = REXML::Document.new xmlstr
      @cells = @doc.elements.to_a('//cell').collect do |c|
        {:col => c.attributes['col'], 
          :row => c.attributes['row'], 
          :formula => c.attributes['formula'],
          :value => c.attributes['value']}
      end
    end
    
    attr_reader :cells
  end
end

# Some versions of the net/http library shipped with earlier versions
# of Ruby didn't have the Delete request defined. We define it
# here if it is missing.
begin
  require 'net/http'
  Net::HTTP::Delete
rescue NameError
  module Net
    class HTTP
      class Delete < HTTPRequest
        METHOD = 'DELETE'
        REQUEST_HAS_BODY = false
        RESPONSE_HAS_BODY = true
      end
    end
  end
end


