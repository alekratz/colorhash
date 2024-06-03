/**
 * Simplified colorhash web frontend.
 */

// TODO - need a way to share palettes between Python and JS

////////////////////////////////////////////////////////////////////////////////
// Colors
////////////////////////////////////////////////////////////////////////////////

class Color {
    constructor() {
        if(new.target === Color) {
            throw new Error("Cannot instantiate abstract class Color");
        }
    }

    toString() { return self.toHTMLColor(); }

    toHTMLColor() { throw new Error("Cannot call abstract method toHTMLColor"); }

    toRGB() { throw new Error("Cannot call abstract method toRGB"); }

    toHSL() { throw new Error("Cannot call abstract method toHSL"); }
}

class RGBColor extends Color {
    constructor(r, g, b) {
        super();
        this.r = r;
        this.g = g;
        this.b = b;
    }

    toHTMLColor() {
        return `rgb(${this.r}, ${this.g}, ${this.b})`;
    }

    toRGB() {
        return this;
    }

    toHSL() {
        // NOTE - this isn't perfect, but it should be OK for our uses.
        // We don't really use the toHSL at all anyway, this is really just here for completeness.
        // example of floating point biting us in the ass:
        // new HSLColor(120, 50, 25).toRGB().toHSL()
        // { h: 120, s: 50, l: 25.098039215686274 }
        let r = this.r / 255;
        let g = this.g / 255;
        let b = this.b / 255;

        let max = Math.max(r, g, b);
        let min = Math.min(r, g, b);

        let h, s;
let l = (max + min) / 2;

        if (max === min) {
            h = s = 0; // achromatic
        } else {
            let d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                // not sure if braces are necessary here, this is mostly just a
                // habit from C/C++ where the `switch` scope is shared
                case r: {
                    h = (g - b) / d + (g < b ? 6 : 0);
                }; break;
                case g: {
                    h = (b - r) / d + 2; 
                }; break;
                case b: {
                    h = (r - g) / d + 4; 
                }; break;
            }
            h /= 6;
        }

        return new HSLColor(h * 360, s * 100, l * 100);
    }
}

class HSLColor extends Color {
    constructor(h, s, l) {
        super();
        this.h = h;
        this.s = s;
        this.l = l;
    }

    toHTMLColor() {
        return `hsl(${this.h}, ${this.s}%, ${this.l}%)`;
    }

    toRGB() {
        // nice little hack we can use to convert to RGB
        const div = document.createElement("div");
        div.style.backgroundColor = this.toHTMLColor();
        const [_, r, g, b] = div
            .style
            .backgroundColor
            .match(/rgb\((\d+), (\d+), (\d+)\)/)
            .map(Number);
        return new RGBColor(r, g, b)
    }

    toHSL() {
        return this;
    };
}

////////////////////////////////////////////////////////////////////////////////
// Utilities
////////////////////////////////////////////////////////////////////////////////

// hahahahahahahaha javascript doesn't even have a zip() function
// HAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHA "JUST INSTALL A DEPENDENCY"
// HAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHA
const zip = (a, b) => a.map((k, i) => [k, b[i]]);

function quantize(min, max, steps) {
    const dist = max - min;
    return Array.from(
        {length: steps},
        (_, i) => min + (i * dist / (steps - 1))
    );
}

/**
 * Converts a hash string to Uint8Array.
 */
function hash2array(hash) {
    return Array.from(
        new Uint8Array(
            hash.match(/../g)
            .map(e => parseInt(e, 16))
        )
    )
}

/**
 * Attempts to detect the type of hash or algorithm that has been supplied.
 * Examples:
 *
 * 'sha1' => 'sha1'
 * 'ae288b06df4a460c37c836e270f9edaabffb7d6d' => 'sha1'
 * 'e575e0af2fbe9d8cc3a2c13542aa1375d2f75875e55529d0889f9b46' => 'sha224'
 * 'md5' => 'md5'
 * 'crc32' => error, not supported
 *
 * etc. 
 */
function detectAlgorithm(hashOrAlgo) {
    const dimensions = {
        md5: 32,
        32: "md5",
        sha1: 40,
        40: "sha1",
        sha224: 56,
        56: "sha224",
        sha256: 64,
        64: "sha256",
        sha384: 96,
        96: "sha384",
        sha512: 128,
        128: "sha512",
    };

    hashOrAlgo = hashOrAlgo.toLowerCase();

    if(hashOrAlgo.match(/^([0-9a-fA-F]{2})+$/)) {
        if(dimensions.hasOwnProperty(hashOrAlgo.length)) {
            return dimensions[hashOrAlgo.length];
        } else {
            return null;
        }
    } else if(dimensions.hasOwnProperty(hashOrAlgo)) {
        return dimensions[hashOrAlgo];
    } else {
        return null;
    }
}

////////////////////////////////////////////////////////////////////////////////
// Palettes
////////////////////////////////////////////////////////////////////////////////

/**
 * Create a list of HSL
 */
function hslPalette(start, end) {
    if(!(start instanceof HSLColor)) {
        throw new TypeError("expected param 'start' to be instance of HSLColor");
    }
    if(!(end instanceof HSLColor)) {
        throw new TypeError("expected param 'end' to be instance of HSLColor");
    }
    const hues = quantize(start.h, end.h, 16);
    const sats = quantize(start.s, end.s, 16);
    const lights = quantize(start.l, end.l, 16);

    return zip(zip(hues, sats), lights).map(
        ([[h, s], l]) => new HSLColor(h, s, l)
    );
}

const GRADIENT_PALETTES = [
    ["red-light", hslPalette(new HSLColor(0, 100, 50), new HSLColor(0, 100, 100))],
    ["red-dark", hslPalette(new HSLColor(0, 100, 0), new HSLColor(0, 100, 50))],
    //
    ["orange-light", hslPalette(new HSLColor(30, 100, 50), new HSLColor(30, 100, 100))],
    ["orange-dark", hslPalette(new HSLColor(30, 100, 0), new HSLColor(30, 100, 50))],
    //
    //["yellow-light", hslPalette(new HSLColor(60, 100, 50), new HSLColor(60, 100, 100))],
    ["yellow-dark", hslPalette(new HSLColor(60, 100, 0), new HSLColor(60, 100, 50))],
    //
    //["lime-light", hslPalette(new HSLColor(90, 100, 50), new HSLColor(90, 100, 100))],
    //["lime-dark", hslPalette(new HSLColor(90, 100, 0), new HSLColor(90, 100, 50))],
    //
    ["green-light", hslPalette(new HSLColor(120, 100, 50), new HSLColor(120, 100, 100))],
    ["green-dark", hslPalette(new HSLColor(120, 100, 0), new HSLColor(120, 100, 50))],
    //
    //["seafoam-light", hslPalette(new HSLColor(150, 100, 50), new HSLColor(150, 100, 100))],
    //["seafoam-dark", hslPalette(new HSLColor(150, 100, 0), new HSLColor(150, 100, 50))],
    //
    ["cyan-light", hslPalette(new HSLColor(180, 100, 50), new HSLColor(180, 100, 100))],
    ["cyan-dark", hslPalette(new HSLColor(180, 100, 0), new HSLColor(180, 100, 50))],
    //
    //["teal-light", hslPalette(new HSLColor(210, 100, 50), new HSLColor(210, 100, 100))],
    //["teal-dark", hslPalette(new HSLColor(210, 100, 0), new HSLColor(210, 100, 50))],
    //
    ["blue-light", hslPalette(new HSLColor(240, 100, 50), new HSLColor(240, 100, 100))],
    ["blue-dark", hslPalette(new HSLColor(240, 100, 0), new HSLColor(240, 100, 50))],
    //
    ["purple-light", hslPalette(new HSLColor(270, 100, 50), new HSLColor(270, 100, 100))],
    ["purple-dark", hslPalette(new HSLColor(270, 100, 0), new HSLColor(270, 100, 50))],
    //
    ["magenta-light", hslPalette(new HSLColor(300, 100, 50), new HSLColor(300, 100, 100))],
    ["magenta-dark", hslPalette(new HSLColor(300, 100, 0), new HSLColor(300, 100, 50))],
    //
    ["pink-light", hslPalette(new HSLColor(330, 100, 50), new HSLColor(330, 100, 100))],
    ["pink-dark", hslPalette(new HSLColor(330, 100, 0), new HSLColor(330, 100, 50))],
    //
    ["gray-light", hslPalette(new HSLColor(0, 0, 50), new HSLColor(0, 0, 100))],
    ["gray-dark", hslPalette(new HSLColor(0, 0, 0), new HSLColor(0, 0, 50))],
];

const MULTICOLOR_PALETTES = [
    ["rainbow", hslPalette(new HSLColor(0, 100, 50), new HSLColor(360, 0, 50))],
    ["rainbow-reverse", hslPalette(new HSLColor(360, 100, 50), new HSLColor(0, 0, 50))],
];

DEFAULT_PALETTES = [].concat(
    GRADIENT_PALETTES,
    MULTICOLOR_PALETTES,
);

////////////////////////////////////////////////////////////////////////////////
// Matricizer
////////////////////////////////////////////////////////////////////////////////

class Matricizer {
    constructor() {
        if(new.target === Matricizer) {
            throw new Error("Cannot instantiate abstract class Matricizer");
        }
    }

    matricize(hash) {
        throw new Error("Cannot call abstract method matricize");
    }

    choosePalette(hash, palettes = null) {
        if(!palettes) {
            palettes = DEFAULT_PALETTES;
        }
        const total = hash2array(hash).reduce((acc, curr) => acc + curr, 0);
        
        return palettes[total % palettes.length][1]
    }

    static chooseDimensions(hashOrAlgo) {
        throw new Error("Cannot call abstract method chooseDimensions");
    }
}

class NibbleMatricizer extends Matricizer {
    constructor() {
        super();
    }

    matricize(hash) {
        const dimensions = {
            md5: [8, 4],
            sha1: [8, 5],
            sha224: [8, 7],
            sha256: [8, 8],
            sha384: [12, 8],
            sha512: [16, 8],
        };

        const hashAlgo = detectAlgorithm(hash);
        if(hashAlgo === null) {
            throw new Error(`unable to determine hash algorithm`);
        }

        const [w, h] = dimensions[hashAlgo];

        const nibbles = hash2array(hash)
            .map(b => [(b & 0xf0) >> 4, b & 0x0f])
            .flat();

        if(nibbles.length != w * h) {
            throw new Error(`invalid hash length: ${hash.length} (${nibbles.length} nibbles)`);
        }
        
        const rows = []
        let cols = []
        for(const b of nibbles) {
            cols.push(b);
            if(cols.length === w) {
                rows.push(cols);
                cols = []
            }
        }
        return rows;
    }

    choosePalette(data, palettes = null) {
        return super.choosePalette(data, palettes || GRADIENT_PALETTES);
    }
}

class RandomartMatricizer extends Matricizer {
    constructor() {
        super();
    }

    matricize(hash) {
        const dimensions = {
            md5: [7, 6],
            sha1: [7, 6],
            sha224: [8, 7],
            sha256: [8, 7],
            sha384: [11, 10],
            sha512: [11, 10],
        }
        
        const hashAlgo = detectAlgorithm(hash);
        if(hashAlgo === null) {
            throw new Error(`unable to determine hash algorithm`);
        }

        const [w, h] = dimensions[hashAlgo];
        const bytes = hash2array(hash);

        // create an empty 2d array
        const rows = Array.from(
            { length: h },
            () => Array.from({ length: w }, () => 0)
        );

        let c = Math.floor(w / 2);
        let r = Math.floor(h / 2);

        // do the randomart algorithm
        for(let value of bytes) {
            for(let i = 0; i < 4; i++) {
                if(value & 1) {
                    c += 1;
                } else {
                    c -= 1;
                }
                if(value & 2) {
                    r += 1;
                } else {
                    r -= 1;
                }
                c = Math.min(Math.max(c, 0), w - 1);
                r = Math.min(Math.max(r, 0), h - 1);
                if(rows[r][c] < 0xf) {
                    rows[r][c] += 1;
                }
                value >>= 2;
            }
        }

        return rows;
    }

    choosePalette(data, palettes = null) {
        return super.choosePalette(data, palettes || MULTICOLOR_PALETTES);
    }
}

////////////////////////////////////////////////////////////////////////////////
// SVG output
////////////////////////////////////////////////////////////////////////////////

function genSVG(matrix, palette, squareSize = 32) {
    const colors = matrix.map(
        row => row.map(v => palette[v])
    );

    const w = colors[0].length;
    const h = colors.length;
    let svg = `<svg width="${w * squareSize}" height="${h * squareSize}" xmlns="http://www.w3.org/2000/svg">\n`;

    for(let r = 0; r < h; r++) {
        for(let c = 0; c < w; c++) {
            const x = c * squareSize;
            const y = r * squareSize;
            const color = colors[r][c];
            svg += `<rect x="${x}" y="${y}" width="${squareSize}" height="${squareSize}" fill="${color.toHTMLColor()}" />\n`;
        }
    }
    svg += "</svg>";
    return svg;
}
