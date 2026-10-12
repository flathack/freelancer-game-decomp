#pragma once
#include "string_cache.hpp"
extern const unsigned short SUBOBJ_ID_NONE;
namespace Archetype { struct Equipment; Equipment* GetEquipment(unsigned int); }

struct EquipDesc {
    unsigned char unknown_00;
    unsigned char padding_01;
    unsigned short id;
    unsigned int arch_id;
    CacheString hardpoint;
    bool equipped;
    unsigned char padding_0d[3];
    float status;
    int count;
    bool temporary;
    unsigned char padding_19[3];
    int owner;
    static const CacheString CARGO_BAY_HP_NAME;
    EquipDesc();
    EquipDesc(const EquipDesc&);
    EquipDesc& operator=(const EquipDesc&);
    bool operator==(const EquipDesc&) const;
    bool operator!=(const EquipDesc&) const;
    bool operator<(const EquipDesc&) const;
    bool operator>(const EquipDesc&) const;
    unsigned short get_id() const;
    void set_id(unsigned short);
    unsigned int get_arch_id() const;
    void set_arch_id(unsigned int);
    const CacheString& get_hardpoint() const;
    void set_hardpoint(const CacheString&);
    bool is_equipped() const;
    void set_equipped(bool);
    float get_status() const;
    void set_status(float);
    int get_count() const;
    void set_count(int);
    bool get_temporary() const;
    void set_temporary(bool);
    int get_owner() const;
    void set_owner(int);
    bool is_internal() const;
    void make_internal();
    float get_cargo_space_occupied() const;
};
#if __SIZEOF_POINTER__==4
static_assert(sizeof(EquipDesc)==32,"Original EquipDesc stride");
static_assert(__builtin_offsetof(EquipDesc,hardpoint)==8,"Hardpoint offset");
static_assert(__builtin_offsetof(EquipDesc,owner)==28,"Owner offset");
#endif
