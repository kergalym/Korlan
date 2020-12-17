      void mainImage() {
        vec4 color = texture(p3d_Texture0, texCoord);
        fragColor = color.bgra;
      }
