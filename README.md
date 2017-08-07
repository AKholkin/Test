There is 2 python scripts for testing: ```test_with_sudo.py``` and ```test.py```. ```test_with_sudo.py``` requires sudo password. To run "test_with_sudo.py" use next command:
```python test_with_sudo.py "sudo password"```

To run "test.py" with is not requires sudo password use next command:
```python test_with_sudo.py```

Test was developed for case when docker container with application is running on server where test will be runnig
