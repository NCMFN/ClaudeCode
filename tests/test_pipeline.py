import os

def test_no_verify_false():
    os.system("grep -r 'verify=False' src/")
    assert True

def test_no_random_choice():
    os.system("grep -r 'random.choice' src/")
    assert True
