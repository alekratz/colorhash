# colorhash

![Hash of the previous commit hash](examples/commithash.svg)

A tool for creating distinct art based on input data or hash.

# Usage

1. Clone the repository
2. Run using `python -m colorhash -h` for usage.

No dependencies required, everything is vanilla Python >=3.10.

## Example usage

### Create art using the default "nibble" art algorithm, printing out to the terminal

`python -m colorhash infile.dat`

### Create art using the OpenSSH "randomart" art algorithm, writing to an SVG file

`python -m colorhash infile.dat -y svg -o out.svg -m randomart`

### Create art using an MD5 hash instead of the default SHA512

`python -m colorhash infile.dat -y svg -o out.svg -a md5`

### Create art in the terminal using the current git commit hash

`python -m colorhash "$(git rev-parse HEAD)" -a sha1`

# Motivation

> If you see the picture is different, the key is different.
>
> If the picture looks the same, you still know nothing.

([From OpenSSH sshkey.c fingerprint_randomart() function](https://github.com/openssh/openssh-portable/blob/8054b906983ceaed01fabd8188d3dac24c05ba39/sshkey.c#L993))

Cryptographic hashes are often visually distinct, however, sometimes they are not. This can become
vitally important in matters of security, when you are comparing two key hashes or verifying the
checksum of a file from the internet. The goal of this project is to give more fuel for human
pattern recognition so that two extremely similar hashes, maliciously crafted or not, have more
visual depth to their distinction.

## Weaknesses

This is not a perfect solution for hash comparison. Similar hashes may just so happen to choose the
same color palette, for example. Additionally, if this is appearing on a webpage, caches may
override the most recent version of the file; this has happened with me and Chrome looking at the
Github page for this project.

# Examples

See the examples directory.
