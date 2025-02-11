The synthetic field is not generated in the JDK 22 because of https://github.com/openjdk/jdk/pull/10797.
It states "It avoids building the lookup table for switches on self" and that is exactly how your [enum `NetworkAddressType`](https://github.com/ldapchai/ldapchai/blob/3a974f829b7022898b031cf1279ae7da0e8566dc/src/main/java/com/novell/ldapchai/impl/AbstractChaiEntry.java#L57) is declared. Code snippet:
```java

        // If enum class is part of this compilation, just switch on ordinal value
        if (enumClass.kind == TYP) {
            final List<Name> idents = enumNamesFor((ClassSymbol)enumClass);
            if (idents != null)
                return new CompileTimeEnumMapping(idents);
        }
```

Reference: https://github.com/ldapchai/ldapchai/issues/32