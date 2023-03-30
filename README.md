# digcli.py

This is a simple client for digitalesregister.it written in python.

## installation

`sudo cp digcli.py /usr/local/bin/`

## getting started

To not have to enter the password every time, edit the source-code
directly and change `json_data` to:
```python
json_data = {
        "username":"<username>",
        "password":"<password>"
}
```

The same is true for the subdomain. To get your subdomain, go to the registry of your school, and copy the string before the first dot and after `https://`.
```python
default_subdomain = '<your_subdomain>'
```

If the names of your lessons are too long, you can change them inside of `short_lesson_name`.
```python
short_lesson_name = {
        "<long_name>":"<shortened_name>"
}
```

You can do the same for teacher names inside `short_teacher_name`.
```python
short_teacher_name = {
        "<long_name>":"<shortened_name>"
}
```
