// https://www.shadertoy.com/view/4ttGWM
// I started working a bit on the colors of Remix 2, ended up with something like this. :)
// Remix 2 here: https://www.shadertoy.com/view/MtcGD7
// Remix 1 here: https://www.shadertoy.com/view/llc3DM
// Original here: https://www.shadertoy.com/view/XsXXRN

float rand(vec2 n) {
    return fract(sin(cos(dot(n, vec2(12.9898,12.1414)))) * 83758.5453);
}

float noise(vec2 n) {
    const vec2 d = vec2(0.0, 1.0);
    vec2 b = floor(n), f = smoothstep(vec2(0.0), vec2(1.0), fract(n));
    return mix(mix(rand(b), rand(b + d.yx), f.x), mix(rand(b + d.xy), rand(b + d.yy), f.x), f.y);
}

float fbm(vec2 n) {
    float total = 0.0, amplitude = 1.0;
    for (int i = 0; i <5; i++) {
        total += noise(n) * amplitude;
        n += n*1.7;
        amplitude *= 0.47;
    }
    return total;
}