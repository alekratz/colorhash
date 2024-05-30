# colorhash

A tool for creating distinct art based on input data or hash.

# Usage

1. Clone the repository
2. Run using `python -m colorhash -h` for usage.

No dependencies required, everything is vanilla Python >=3.10.

## Example usage

### Create art using the default "nibble" art algorithm

`python -m colorhash infile.dat -o out.svg`

### Create art using the OpenSSH "randomart" art algorithm

`python -m colorhash infile.dat -o out.svg -m randomart`

### Create art using an MD5 hash instead of the default SHA512

`python -m colorhash infile.dat -o out.svg -a md5`

# Motivation

Cryptographic hashes are often visually distinct, however, sometimes they are not. This can become
vitally important in matters of security, when you are comparing two key hashes or verifying the
checksum of a file from the internet. The goal of this project is to give more fuel for human
pattern recognition so that two extremely similar hashes, maliciously crafted or not, have more
visual depth to their distinction.

This is not a perfect solution. [From OpenSSH sshkey.c](https://github.com/openssh/openssh-portable/blob/8054b906983ceaed01fabd8188d3dac24c05ba39/sshkey.c#L993):

> If you see the picture is different, the key is different.
> If the picture looks the same, you still know nothing.

# Examples

See the examples directory. TODO : make these into PNGs and embed them in this README file.