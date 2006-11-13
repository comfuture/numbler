dojo.require("dojo.crypto.Blowfish");

function test_Blowfish_encryption(){
	var message = "The rain in Spain falls mainly on the plain.";
	var key = "foobar";
	var base64Encrypted = "WI5J5BPPVBuiTniVcl7KlIyNMmCosmKTU6a/ueyQuoUXyC5dERzwwdzfFsiU4vBw";
	result = dojo.crypto.Blowfish.encrypt(message, key);
	jum.assertEquals("BlowfishEncryption", base64Encrypted, result);
}

function test_Blowfish_decryption(){
	var message = "The rain in Spain falls mainly on the plain.";
	var key = "foobar";
	var base64Encrypted = "WI5J5BPPVBuiTniVcl7KlIyNMmCosmKTU6a/ueyQuoUXyC5dERzwwdzfFsiU4vBw";

	result = dojo.crypto.Blowfish.decrypt(base64Encrypted, key);
	jum.assertEquals("BlowfishDecryption", message, result);
}
