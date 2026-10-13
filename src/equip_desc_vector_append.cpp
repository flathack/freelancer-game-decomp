#include "equip_desc_collections.hpp"
extern "C" void* loadout_map_allocate(unsigned int);
extern "C" void loadout_map_free(void*);
static unsigned int length(const EquipDesc* first,const EquipDesc* last){return first?(reinterpret_cast<unsigned int>(last)-reinterpret_cast<unsigned int>(first))/32:0;}
static void copy_fields(EquipDesc* out,const EquipDesc* in){
 if(!out)return;
 for(unsigned int i=0;i<32;++i)if(i!=1 && !(i>=13 && i<=15) && !(i>=25 && i<=27))reinterpret_cast<unsigned char*>(out)[i]=reinterpret_cast<const unsigned char*>(in)[i];
}
void EquipDescVector::append(const EquipDescVector& other){
 unsigned int old=length(begin,end),total=old+length(other.begin,other.end);
 if(length(begin,capacity)<total){
  EquipDesc* fresh=static_cast<EquipDesc*>(loadout_map_allocate(total*32));
  for(unsigned int i=0;i<old;++i)copy_fields(fresh+i,begin+i);
  loadout_map_free(begin);capacity=reinterpret_cast<EquipDesc*>(reinterpret_cast<unsigned int>(fresh)+total*32);
  end=reinterpret_cast<EquipDesc*>(reinterpret_cast<unsigned int>(fresh)+old*32);begin=fresh;
 }
 // Original re-reads source end after each insertion. Self-append can therefore
 // keep extending its own loop bound; do not silently snapshot the initial end.
 for(const EquipDesc* item=other.begin;item!=other.end;++item)add_equipment_item(*item,false);
}
