

public class InvokeInterfaceToInvokeVirtual {

    public static void main(String[] args) {
        NodeVisitor inOrderVisitor = new InOrder();
        inOrderVisitor.visit(new Node(1));
        System.out.println(inOrderVisitor.toString());

    }

    private static class InOrder implements NodeVisitor {
        @Override
        public void visit(Node node) {
            if (node.left != null) {
                node.left.accept(this);
            }
            System.out.println(node.value);
            if (node.right != null) {
                node.right.accept(this);
            }
        }
    }
}



interface  NodeVisitor {
    void visit(Node node);
}

class Node {
    int value;
    Node left;
    Node right;
    Node(int value) {
        this.value = value;
    }

    void accept(NodeVisitor visitor) {
        visitor.visit(this);
    }
}
