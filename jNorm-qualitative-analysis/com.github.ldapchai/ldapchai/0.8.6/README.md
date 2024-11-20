Invocation of `.getClass()` in WireTracerWrapper.class is replaced
```diff
-        45: invokeinterface #49,  1           // InterfaceMethod com/novell/ldapchai/provider/ChaiProviderImplementor.getClass:()Ljava/lang/Class;
+        45: invokevirtual #49                 // Method java/lang/Object.getClass:()Ljava/lang/Class;
```

Rebuilding the project with JDK 8 failed the build.

The order of statments and arguments in `ApacheLdapProviderImpl$2` is switched.

```diff
   ApacheLdapProviderImpl$2(final ApacheLdapProviderImpl this$0, final org.apache.directory.api.ldap.model.message.ExtendedResponse var2) {
-      this.val$apacheResponse = var2;
      this.this$0 = this$0;
+      this.val$apacheResponse = var2;
   }
```

In `AbstractChaiEntry.java`, the `readNetAddressAttribute` method has a huge diff.
Majorly, it seems that lookupswitch is organized differently in bytecode. 
Why 'getstatic' is called here `1.$SwitchMap$com$novell$ldapchai$impl$AbstractChaiEntry$NetworkAddressType[type.ordinal()]`
In the other version, it is only `.ordinal()`.
Also in `HashSaltAnswer.java`, the switch has a similar issue.
