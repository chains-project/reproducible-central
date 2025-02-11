import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.function.Function;


// https://github.com/langchain4j/langchain4j/blob/a8ad9e48d9e473164ff6f7c4219bea777f8e5e8e/langchain4j-core/src/test/java/dev/langchain4j/internal/ValidationUtilsTest.java#L59-L62
public class Checkcast {
    public static void main(String[] args) {
        Function<Void, Void> m = (v) -> {
            List<String> list = new ArrayList<>();
            list.add("a");
            list.add("b");
            list.add("c");
            ensureNotEmpty(list, "list");
            return null;
        };  
    }


    public static <T extends Collection<?>> T ensureNotEmpty(T collection, String name) {
        if (collection == null || collection.isEmpty()) {
            throw new IllegalArgumentException("cannot be null or empty");
        }

        return collection;
    }
    
}
