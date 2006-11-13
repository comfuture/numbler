
JSAN.errorLevel = 'die';
//JSAN.addRepository('tools').use("Test.Builder");
JSAN.addRepository('tools').use("Test.More");
JSAN.addRepository("..");
JSAN.addRepository("../..").use("MochiKit.Base");
//JSAN.addRepository("..").use("RedBlackNode");
//JSAN.addRepository("..").use("RedBlackTree");
JSAN.addRepository("../..").use("LiveSheet.dimManager");
JSAN.require("RedBlackNode");
JSAN.require("RedBlackTree");
	
//var test = new Test.More.builder();
plan({ tests: 53}); // is this ignored?

 var manager = new LiveSheet.dimManager (50,50);
// // add some data
//document.write('creating column data...');
manager.addColumnWidth(5,200);
manager.addColumnWidth(12,200);
isDeeply([5,12],manager.dumpCols(),'verifying number of columns');

ok(manager.findCol(5).startval == 200,'checking column width for column 5');
ok(manager.findCol(12).startval == 700,'checking column width for column 5');

// update the column width of 5 and verify the change propagation

manager.addColumnWidth(5,10);
ok(manager.findCol(5).end() == 210,'verify end of changed column 5');
ok(manager.findCol(12).startval == 510,'verify end of changed column 5');

// test insert before
manager.addColumnWidth(2,40);
ok(manager.findCol(5).end() == 200,'verify shrunken end for column 5');

// test insert at end
manager.addColumnWidth(35,100);
ok(manager.findCol(35).startval == 1800,'verify startval at end insertion');

// test that a value not in the tree comes up with the correct column calculation
var result = manager.coldims(6).startval;
ok(result == 200,'verify start of column not in tree,got ' + result);

ok(manager.coldims(1).startval  == 0,'checking column 1 start value');
ok(manager.coldims(1).end()  == 50,'checking column 1 start value');

//verify that the startval is always as same as the previous row.
for(var i=0;i<100;i++) {
	var col = Math.floor(Math.random()*100);
	if(col >= 2) {
		ok(manager.coldims(col).startval == manager.coldims(col-1).end(),
			 'checking end matches start');
	}
 };

// test cases for empty trees
ok(new LiveSheet.dimManager(50,50).coldims(40).startval==1950,'test case for empty trees')

// test caes for trees with one value



// test that you can't insert a column or row at 0, cols > 255, rows > 65535
// test findStartAndEndcode

// test edge cases (1,65535)
// test that you can't insert a column width or row width for 0



// document.write('done with columns');





