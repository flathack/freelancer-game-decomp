# CSimple: erste Rekonstruktion

Baseline: `analysis/targets.json` bindet die Analyse an den SHA-256 von `common.dll`.
ImageBase: `0x06260000`; x86 PE, Linkerkennung `6.24`.

| Export | RVA | VA | Interpretation |
|---|---|---|---|
| `?get_id@CSimple@@QBEABIXZ` | `0x215a0` | `0x062815a0` | `lea eax,[ecx+0xb0]; ret` |
| `?get_type@CSimple@@QBEIXZ` | `0x215b0` | `0x062815b0` | `mov eax,[ecx+0xe0]; ret` |

Microsoft-C++-Namensdekoration und Maschinenbefehle stützen:
`get_id()` liefert eine Referenz auf einen unsigned-int-Wert, `get_type()` einen
unsigned-int-Wert. `ecx` enthält den this-Zeiger. Beide sind const-Methoden.

Die unbekannten Bereiche im C++-Layout sind Platzhalter. Basisklassen, virtuelle
Methoden, weitere Member und die Gesamtgröße sind noch nicht rekonstruiert.
Dieses Layout darf deshalb nicht als vollständige interoperable Klasse gelten.

Funktionsgrenzen: jeweils 7 Bytes einschließlich bedingungslosem `ret`, anschließend
Alignment bis zur nächsten Funktion. Der Originalcode verwendet `0x90`-Padding,
Clang mehrbyteige NOPs; dieses Padding wird nicht als Funktionscode gezählt.
Die beiden Methoden besitzen keine relativen Aufrufe oder Datenrelokationen.
