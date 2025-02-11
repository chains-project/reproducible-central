// https://github.com/ldapchai/ldapchai/blob/a9de4ccc8db9a4862f3819f3dfb63e57a6450bdf/src/main/java/com/novell/ldapchai/impl/AbstractChaiEntry.java#L122
public abstract  class InvokeInterfaceToInvokeVirtual implements ChaiEntry {
    protected A chaiProvider;
    protected String entryDN;

    public InvokeInterfaceToInvokeVirtual( final String entryDN, final A chaiProvider )
    {
        this.chaiProvider = chaiProvider;
        this.entryDN = entryDN == null ? "" : entryDN;
    }
    
    public boolean equals( final Object o )
    {
        if ( this == o )
        {
            return true;
        }
        if ( !( o instanceof ChaiEntry ) )
        {
            return false;
        }

        final InvokeInterfaceToInvokeVirtual chaiEntry = ( InvokeInterfaceToInvokeVirtual ) o;

        return !( chaiProvider != null
                ? !chaiProvider.equals( chaiEntry.chaiProvider )
                : chaiEntry.chaiProvider != null ) && !( entryDN != null
                ? !entryDN.equals( chaiEntry.entryDN )
                : chaiEntry.entryDN != null
        );
    }
}

interface ChaiEntry {}

class A { }
