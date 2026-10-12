#include "equip_desc.hpp"
EquipDesc::EquipDesc() : unknown_00(0),id(SUBOBJ_ID_NONE),arch_id(0),hardpoint(CARGO_BAY_HP_NAME),equipped(false),status(1.0f),count(1),temporary(false),owner(0) {}
EquipDesc::EquipDesc(const EquipDesc& o) : unknown_00(o.unknown_00),id(o.id),arch_id(o.arch_id),hardpoint(o.hardpoint),equipped(o.equipped),count(o.count),temporary(o.temporary),owner(o.owner) {
    // Preserve raw float bits as the original integer MOV instructions do.
    __builtin_memcpy(&status,&o.status,sizeof(status));
}
EquipDesc& EquipDesc::operator=(const EquipDesc& o) {
    // Original assignment copies all 32 bytes, including padding.
    if(this!=&o) __builtin_memcpy(static_cast<void*>(this),static_cast<const void*>(&o),sizeof(EquipDesc));
    return *this;
}
bool EquipDesc::operator==(const EquipDesc& o) const { return id==o.id; }
bool EquipDesc::operator!=(const EquipDesc& o) const { return id!=o.id; }
bool EquipDesc::operator<(const EquipDesc& o) const { return id<o.id; }
bool EquipDesc::operator>(const EquipDesc& o) const { return id>o.id; }
unsigned short EquipDesc::get_id() const { return id; }
void EquipDesc::set_id(unsigned short v) { id=v; }
unsigned int EquipDesc::get_arch_id() const { return arch_id; }
void EquipDesc::set_arch_id(unsigned int v) { arch_id=v; }
const CacheString& EquipDesc::get_hardpoint() const { return hardpoint; }
void EquipDesc::set_hardpoint(const CacheString& v) { hardpoint=v; }
bool EquipDesc::is_equipped() const { return equipped; }
void EquipDesc::set_equipped(bool v) { equipped=v; }
float EquipDesc::get_status() const { return status; }
void EquipDesc::set_status(float v) { __builtin_memcpy(&status,&v,sizeof(v)); }
int EquipDesc::get_count() const { return count; }
void EquipDesc::set_count(int v) { count=v; }
bool EquipDesc::get_temporary() const { return temporary; }
void EquipDesc::set_temporary(bool v) { temporary=v; }
int EquipDesc::get_owner() const { return owner; }
void EquipDesc::set_owner(int v) { owner=v; }
bool EquipDesc::is_internal() const { return hardpoint.value==CARGO_BAY_HP_NAME.value; }
void EquipDesc::make_internal() { hardpoint=CARGO_BAY_HP_NAME; }
#if defined(_WIN32) && defined(_M_IX86) && defined(__clang__)
// Temporary ABI shim: the original returns unrounded extended precision in ST0.
// Clang's ordinary float-returning C++ body rounds to binary32 before returning.
// Keep the decision and lookup in C++; preserve the x87 operation at the boundary.
extern "C" int __fastcall equipdesc_has_cargo(const EquipDesc* self) {
    return self->is_internal() && self->arch_id;
}
extern "C" Archetype::Equipment* __fastcall equipdesc_cargo_equipment(const EquipDesc* self) {
    return Archetype::GetEquipment(self->arch_id);
}
// ECX carries this; the symbol name is the original member-function ABI.
extern "C" float __fastcall equipdesc_cargo_space_abi(const EquipDesc*)
    __asm__("?get_cargo_space_occupied@EquipDesc@@QBEMXZ");
extern "C" __declspec(naked) float __fastcall equipdesc_cargo_space_abi(const EquipDesc*) {
    __asm {
        push esi
        mov esi, ecx
        call equipdesc_has_cargo
        test eax, eax
        jz no_cargo
        mov ecx, esi
        call equipdesc_cargo_equipment
        fild dword ptr [esi + 14h]
        fmul dword ptr [eax + 5ch]
        pop esi
        ret
    no_cargo:
        fldz
        pop esi
        ret
    }
}
#else
float EquipDesc::get_cargo_space_occupied() const {
    if(!is_internal() || !arch_id) return 0.0f;
    Archetype::Equipment* equipment=Archetype::GetEquipment(arch_id);
    const float* volume=reinterpret_cast<const float*>(reinterpret_cast<const unsigned char*>(equipment)+0x5c);
    return static_cast<double>(count)*static_cast<double>(*volume);
}
#endif
