// Six original exports alias one ID_String word accessor at VA 0x062f11d0.
struct ID_String { unsigned int value; };
namespace Archetype {
unsigned int GetAsteroidID(const ID_String& id){return id.value;}
unsigned int GetDynamicAsteroidID(const ID_String& id){return id.value;}
unsigned int GetEquipmentID(const ID_String& id){return id.value;}
unsigned int GetShipID(const ID_String& id){return id.value;}
unsigned int GetSimpleID(const ID_String& id){return id.value;}
unsigned int GetSolarID(const ID_String& id){return id.value;}
}
