from wells.hash_log import hash_log

image1 = open('tests/images/1.tiff', 'rb').read()
image2 = open('tests/images/2.tiff', 'rb').read()

def test_returns_string():
    hash_value = hash_log(image1)
    assert isinstance(hash_value, str)

def test_consistent_hash():
    hash_value_1 = hash_log(image1)
    hash_value_2 = hash_log(image1)
    assert hash_value_1 == hash_value_2

def test_unique_hash():
    hash_value_1 = hash_log(image1)
    hash_value_2 = hash_log(image2)
    assert hash_value_1 != hash_value_2
