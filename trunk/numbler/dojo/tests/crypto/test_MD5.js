dojo.require("dojo.crypto.MD5");

function test_MD5_compute(){
	//	TODO: tests for HMAC calculation
	var message = "The rain in Spain falls mainly on the plain.";
	var base64 = "OUhxbVZ1Mtmu4zx9LzS5cA==";
	var hex = "3948716d567532d9aee33c7d2f34b970";
	var s = "9HqmVu2\xD9\xAE\xE3<}/4\xB9p";

	var result = dojo.crypto.MD5.compute(message);
	jum.assertEquals("MD5:toBase64", base64, result);
	
	var result = dojo.crypto.MD5.compute(message, dojo.crypto.MD5.outputTypes.Hex);
	jum.assertEquals("MD5:toHex", hex, result);
	
	var result = dojo.crypto.MD5.compute(message, dojo.crypto.MD5.outputTypes.String);
	jum.assertEquals("MD5:toString", s, result);
}
