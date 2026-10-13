#include "equip_desc_collections.hpp"
extern "C" void* loadout_map_allocate(unsigned int);
extern "C" void loadout_map_free(void*);
extern "C" int equip_collection_compare(const char*,const char*);
static void construct(EquipDesc* out,const EquipDesc* in){
 if(!out)return;
 for(unsigned int i=0;i<32;++i)if(i!=1 && !(i>=13 && i<=15) && !(i>=25 && i<=27))reinterpret_cast<unsigned char*>(out)[i]=reinterpret_cast<const unsigned char*>(in)[i];
}
static unsigned int length(const EquipDesc* a,const EquipDesc* b){return a?(reinterpret_cast<unsigned int>(b)-reinterpret_cast<unsigned int>(a))/32:0;}
int EquipDescVector::add_equipment_item(const EquipDesc& value,bool combine){
 if(combine){
  for(;;){
   EquipDesc* item=begin;
   while(item!=end && item->arch_id!=value.arch_id)++item;
   if(item==end)break;
   if(reinterpret_cast<unsigned char*>(item)[24]!=reinterpret_cast<const unsigned char*>(&value)[24] || item->owner!=value.owner || equip_collection_compare(item->hardpoint.value,value.hardpoint.value)!=0)continue;
   unsigned int count=static_cast<unsigned int>(item->count)+static_cast<unsigned int>(value.count);
   if(item->status<1.0f){
    if(!(value.status<1.0f)){item->count=static_cast<int>(count);return 1;}
    double sum=static_cast<double>(item->status)+static_cast<double>(value.status);
    if(sum>=1.0){item->status=static_cast<float>(sum-1.0);item->count=static_cast<int>(count);}
    else {item->status=static_cast<float>(sum);item->count=static_cast<int>(count-1);}
   }else{
    item->count=static_cast<int>(count);volatile float converted=value.status;item->status=converted;
   }
   return 1;
  }
 }
 if(end==capacity){
  unsigned int old=length(begin,end),growth=old>=2?old:1;
  EquipDesc* fresh=static_cast<EquipDesc*>(loadout_map_allocate((old+growth)*32));
  for(unsigned int i=0;i<old;++i)construct(fresh+i,begin+i);
  construct(fresh+old,&value);loadout_map_free(begin);
  begin=fresh;end=reinterpret_cast<EquipDesc*>(reinterpret_cast<unsigned int>(fresh)+(old+1)*32);capacity=reinterpret_cast<EquipDesc*>(reinterpret_cast<unsigned int>(fresh)+(old+growth)*32);
 }else{construct(end,&value);++end;}
 return 0;
}
