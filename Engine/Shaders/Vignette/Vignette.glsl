#version 120

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
	vec2 uv = fragCoord.xy / iResolution.xy;

    uv *=  1.0 - uv.yx;   //vec2(1.0)- uv.yx; -> 1.-u.yx;

    float vig = uv.x*uv.y * 15.0; // multiply with sth for intensity

    vig = pow(vig, 0.25); // change pow for modifying the extend of the  vignette


    fragColor = vec4(vig);
}