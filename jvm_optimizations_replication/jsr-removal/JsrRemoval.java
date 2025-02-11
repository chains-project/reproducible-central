import java.io.IOException;
import java.io.InputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

// https://github.com/raphw/byte-buddy/blob/59554f85835186a693dbadf6092a01bc755049a0/byte-buddy-dep/src/main/java/net/bytebuddy/dynamic/ClassFileLocator.java#L1175
public class JsrRemoval {
    public boolean  locate(ZipFile name) throws IOException {
        ZipEntry zipEntry = name.getEntry("classes/" + name.toString().replace('.', '/') + ".class");
        if (zipEntry == null) {
            return false;
        } else {
            InputStream inputStream = name.getInputStream(zipEntry);
            try {
                return inputStream.read() != -1;
            } finally {
                inputStream.close();
            }
        }
    }
}
