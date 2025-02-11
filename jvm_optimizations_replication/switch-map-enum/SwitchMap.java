// https://github.com/ldapchai/ldapchai/blob/3a974f829b7022898b031cf1279ae7da0e8566dc/src/main/java/com/novell/ldapchai/impl/AbstractChaiEntry.java#L57
public class SwitchMap {
    private enum Color {
        RED
    }

    public static void main(String[] args) {
        switch (Enum.valueOf(Color.class, args[0])) {
            case RED:
                System.out.println("Red");
                break;
            default:
                System.out.println("Unknown");
        }
    }
}
