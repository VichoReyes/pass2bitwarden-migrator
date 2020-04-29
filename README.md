# pass to Bitwarden migrator

This is a small, customizable script to generate a csv file in
the [Bitwarden format](https://bitwarden.com/help/article/import-data/)
from a [zx2c4 password store](https://www.passwordstore.org/).

The only dependencies needed are python 3.6+, a working
installation of `pass` and GNU `find` (I think).

## Running

```
$ python migrator.py | tee passwords.csv
```

## Customization

If you think your `pass` directory structure is unconventional,
the most important part of the program is the `create_elem` function.
Adapt that function to your needs and run the program.

## Contributing

If you feel like your changes can be useful to more people,
feel free to open a pull request.