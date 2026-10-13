#include "loadout_map.hpp"
static unsigned int size_of(const EquipDesc* first,const EquipDesc* last) {
 return first?(reinterpret_cast<unsigned int>(last)-reinterpret_cast<unsigned int>(first))/32:0;
}
static void construct(EquipDesc* out,const EquipDesc* in) {
 if(!out)return;
 const unsigned char* source=reinterpret_cast<const unsigned char*>(in);unsigned char* target=reinterpret_cast<unsigned char*>(out);
 for(unsigned int i=0;i<32;++i)if(i!=1 && !(i>=13 && i<=15) && !(i>=25 && i<=27))target[i]=source[i];
}
static void assign(EquipDesc* out,const EquipDesc* in) {
 for(unsigned int i=0;i<32;i+=4){unsigned int word;__builtin_memcpy(&word,reinterpret_cast<const unsigned char*>(in)+i,4);__builtin_memcpy(reinterpret_cast<unsigned char*>(out)+i,&word,4);}
}
namespace Loadout {
Map::Map(const Map& source):id(source.id),ids(source.ids) {
 allocator[0]=source.allocator[0];unsigned int count=size_of(source.begin,source.end);
 begin=static_cast<EquipDesc*>(loadout_map_allocate(count*32));
 for(unsigned int i=0;i<count;++i)construct(begin+i,source.begin+i);
 end=reinterpret_cast<EquipDesc*>(reinterpret_cast<unsigned int>(begin)+count*32);capacity=end;
}
Map& Map::operator=(const Map& source) {
 id=source.id;
 if(this!=&source){
  unsigned int count=size_of(source.begin,source.end),old=size_of(begin,end),space=size_of(begin,capacity);
  if(old<count && space<count){
   loadout_map_free(begin);begin=static_cast<EquipDesc*>(loadout_map_allocate(count*32));
   for(unsigned int i=0;i<count;++i)construct(begin+i,source.begin+i);
   end=reinterpret_cast<EquipDesc*>(reinterpret_cast<unsigned int>(begin)+count*32);capacity=end;
  } else {
   for(unsigned int i=0;i<count;++i)if(i<old)assign(begin+i,source.begin+i);else construct(begin+i,source.begin+i);
   end=reinterpret_cast<EquipDesc*>(reinterpret_cast<unsigned int>(begin)+count*32);
  }
 }
 ids=source.ids;return *this;
}
Map::~Map(){loadout_map_free(begin);
 // Preserve original post-destruction clearing despite compiler dead-store removal.
 EquipDesc* volatile* fields=reinterpret_cast<EquipDesc* volatile*>(&begin);
 fields[0]=nullptr;fields[1]=nullptr;fields[2]=nullptr;
}
}
