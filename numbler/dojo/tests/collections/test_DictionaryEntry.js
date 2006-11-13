dojo.require("dojo.collections.Collections");
function test_DictionaryEntry(){
	var d = new dojo.collections.DictionaryEntry("foo","bar");
	jum.assertEquals("DictionaryEntry.valueOf", "bar", d.valueOf());
	jum.assertEquals("DictionaryEntry.toString", "bar", d.toString());
}
