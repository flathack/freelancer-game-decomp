#include "archetype_ownership.hpp"
#include "loadout_tree.hpp"
extern "C" { extern Loadout::LookupTree EquipmentArchetypeTree; }
// 063015d0: real unsigned tree lookup used by Equipment::read's inherit path.
// The previously published reader's diagnostic/missing/null split is unchanged.
extern "C" void* arch_inherit_node(ArchWord id) {
    auto* candidate=EquipmentArchetypeTree.head;
    auto* node=candidate->parent;
    while (node!=EquipmentArchetypeTree.nil) {
        if (node->key<id) node=node->right;
        else { candidate=node; node=node->left; }
    }
    return candidate==EquipmentArchetypeTree.head || id<candidate->key
        ? EquipmentArchetypeTree.head : candidate;
}
extern "C" void* arch_inherit_sentinel() { return EquipmentArchetypeTree.head; }
using byte = unsigned char;
using Word = unsigned int;
static Word& word(void* p, Word o) { return *reinterpret_cast<Word*>(static_cast<byte*>(p)+o); }
static Word word(const void* p, Word o) { return *reinterpret_cast<const Word*>(static_cast<const byte*>(p)+o); }
static byte& octet(void* p, Word o) { return *(static_cast<byte*>(p)+o); }
static byte octet(const void* p, Word o) { return *(static_cast<const byte*>(p)+o); }
static void vptr(void* p, const void* slots) { *static_cast<volatile Word*>(p)=reinterpret_cast<Word>(slots); }
static void words(void* d, const void* s, Word first, Word last) {
    for (Word o=first; o<=last; o+=4) word(d,o)=word(s,o);
}
static void client_call(Word p, Word slot) {
    if (p) {
        using Call=void(__thiscall*)(void*);
        const auto table=*reinterpret_cast<Call**>(p);
        table[slot](reinterpret_cast<void*>(p));
    }
}
struct Node { Node *left,*parent,*right; byte payload[52]; byte color,nil,padding[2]; };
struct Tree { byte allocator[4]; Node *head,*nil; byte state[4]; Word count; };
static_assert(sizeof(Node)==0x44 && __builtin_offsetof(Node,color)==0x40,"original Root node");
static_assert(sizeof(Tree)==0x14,"original Root tree");
static Tree* tree(void* p) { return reinterpret_cast<Tree*>(static_cast<byte*>(p)+0x48); }
static const Tree* tree(const void* p) { return reinterpret_cast<const Tree*>(static_cast<const byte*>(p)+0x48); }
static Word vector_size(const void* p) {
    const Word begin=word(p,4);
    return begin ? static_cast<Word>(static_cast<int>(word(p,8)-begin)>>2) : 0;
}
// 062fb660: pointer elements are copied, but the owned allocation is not aliased.
extern "C" void* __thiscall archetype_pointer_vector_assign(void* d, const void* s) {
    if (d==s) return d;
    Word n=vector_size(s), old=vector_size(d), begin=word(d,4);
    Word source=word(s,4), end=word(s,8);
    if (n<=old) {
        Word out=begin;
        for (Word p=source;p!=end;p+=4,out+=4) word(reinterpret_cast<void*>(out),0)=word(reinterpret_cast<const void*>(p),0);
        word(d,8)=word(d,4)+4*vector_size(s);
    } else {
        Word capacity=begin ? static_cast<Word>(static_cast<int>(word(d,12)-begin)>>2) : 0;
        if (n<=capacity) {
            Word p=source,out=begin, split=source+4*old;
            for (;p!=split;p+=4,out+=4) word(reinterpret_cast<void*>(out),0)=word(reinterpret_cast<const void*>(p),0);
            out=word(d,8);
            for (;p!=end;p+=4,out+=4) if (out) word(reinterpret_cast<void*>(out),0)=word(reinterpret_cast<const void*>(p),0);
            word(d,8)=word(d,4)+4*vector_size(s);
        } else {
            arch_runtime_free(reinterpret_cast<void*>(begin));
            n=vector_size(s);
            Word length=static_cast<int>(n)<0 ? 0 : n;
            Word out=reinterpret_cast<Word>(arch_runtime_allocate(length*4));
            word(d,4)=out;
            for (Word p=word(s,4);p!=word(s,8);p+=4,out+=4)
                if (out) word(reinterpret_cast<void*>(out),0)=word(reinterpret_cast<const void*>(p),0);
            word(d,12)=out; word(d,8)=out;
        }
    }
    return d;
}
// 06280e50: field-wise node payload construction, preserving padding.
static void payload_copy(void* d, const void* s) {
    if (!d) return;
    word(d,0)=word(s,0); octet(d,4)=octet(s,4); word(d,8)=word(s,8);
    words(d,s,12,32); octet(d,36)=octet(s,36);
    Word n=vector_size(static_cast<const byte*>(s)+36);
    if (static_cast<int>(n)<0) n=0;
    Word out=reinterpret_cast<Word>(arch_runtime_allocate(n*4));
    word(d,40)=out;
    for (Word p=word(s,40);p!=word(s,44);p+=4,out+=4)
        if (out) word(reinterpret_cast<void*>(out),0)=word(reinterpret_cast<const void*>(p),0);
    word(d,44)=out; word(d,48)=out;
}
// 06280660 + 06343d80/06343d40. External payload handles intentionally retain
// the original shallow semantics, unlike the separately owned vector buffer.
static void payload_destroy(void* p) {
    Word handle=word(p,8);
    if (handle) arch_runtime_payload_heap_free(reinterpret_cast<void*>(word(reinterpret_cast<const void*>(handle),static_cast<Word>(-4))));
    arch_runtime_free(reinterpret_cast<void*>(word(p,40)));
    word(p,40)=0; word(p,44)=0; word(p,48)=0;
}
static Node* node_allocate(Node* parent, byte color) {
    auto* n=static_cast<Node*>(arch_runtime_allocate(0x44));
    n->parent=parent; n->color=color; n->nil=0; return n;
}
// 062fd090: preserve root-left-right allocation order and marker semantics.
static Node* clone(Tree* d, const Node* s, Node* parent) {
    Node* result=d->nil;
    if (!s->nil) {
        Node* n=node_allocate(parent,s->color);
        payload_copy(n->payload,s->payload);
        n->left=d->nil; n->right=d->nil;
        if (result==d->nil) result=n;
        n->left=clone(d,s->left,n); n->right=clone(d,s->right,n);
    }
    return result;
}
// 062fc530: right subtree, current node, then left descent.
static void destroy_subtree(Tree* t, Node* p) {
    while (p!=t->nil) {
        destroy_subtree(t,p->right);
        Node* left=p->left;
        payload_destroy(p->payload); arch_runtime_free(p); p=left;
    }
}
static Node* minimum(Node* p) { while (!p->left->nil) p=p->left; return p; }
static Node* maximum(Node* p) { while (!p->right->nil) p=p->right; return p; }
static Node* next(Node* p) {
    if (!p->right->nil) return minimum(p->right);
    Node* parent=p->parent;
    while (p==parent->right) { p=parent; parent=parent->parent; }
    if (p->right!=parent) p=parent;
    return p;
}
static void rotate_left(Tree* t,Node* x) {
    Node* y=x->right; x->right=y->left;
    if (y->left!=t->nil) y->left->parent=x;
    y->parent=x->parent;
    if (x==t->head->parent) t->head->parent=y;
    else if (x==x->parent->left) x->parent->left=y; else x->parent->right=y;
    y->left=x; x->parent=y;
}
static void rotate_right(Tree* t,Node* x) {
    Node* y=x->left; x->left=y->right;
    if (y->right!=t->nil) y->right->parent=x;
    y->parent=x->parent;
    if (x==t->head->parent) t->head->parent=y;
    else if (x==x->parent->right) x->parent->right=y; else x->parent->left=y;
    y->right=x; x->parent=y;
}
// 062fc150 erase path, also used by the original when count==0 but links exist.
static void erase(Tree* t,Node* z) {
    Node* y=z; Node* x;
    if (y->left==t->nil) x=y->right;
    else if (y->right==t->nil) x=y->left;
    else { y=minimum(y->right); x=y->right; }
    if (y!=z) {
        z->left->parent=y; y->left=z->left;
        if (y==z->right) x->parent=y;
        else { x->parent=y->parent; y->parent->left=x; y->right=z->right; z->right->parent=y; }
        if (t->head->parent==z) t->head->parent=y;
        else if (z->parent->left==z) z->parent->left=y; else z->parent->right=y;
        y->parent=z->parent; byte c=y->color; y->color=z->color; z->color=c; y=z;
    } else {
        x->parent=y->parent;
        if (t->head->parent==z) t->head->parent=x;
        else if (z->parent->left==z) z->parent->left=x; else z->parent->right=x;
        if (t->head->left==z) t->head->left=z->right==t->nil ? z->parent : minimum(x);
        if (t->head->right==z) t->head->right=z->left==t->nil ? z->parent : maximum(x);
    }
    if (y->color==1) {
        while (x!=t->head->parent && x->color==1) {
            if (x==x->parent->left) {
                Node* w=x->parent->right;
                if (w->color==0) { w->color=1; x->parent->color=0; rotate_left(t,x->parent); w=x->parent->right; }
                if (w->left->color==1 && w->right->color==1) { w->color=0; x=x->parent; }
                else {
                    if (w->right->color==1) { w->left->color=1; w->color=0; rotate_right(t,w); w=x->parent->right; }
                    w->color=x->parent->color; x->parent->color=1; w->right->color=1; rotate_left(t,x->parent); break;
                }
            } else {
                Node* w=x->parent->left;
                if (w->color==0) { w->color=1; x->parent->color=0; rotate_right(t,x->parent); w=x->parent->left; }
                if (w->right->color==1 && w->left->color==1) { w->color=0; x=x->parent; }
                else {
                    if (w->left->color==1) { w->right->color=1; w->color=0; rotate_left(t,w); w=x->parent->left; }
                    w->color=x->parent->color; x->parent->color=1; w->left->color=1; rotate_right(t,x->parent); break;
                }
            }
        }
        x->color=1;
    }
    payload_destroy(y->payload); arch_runtime_free(y); --t->count;
}
static void clear(Tree* t) {
    Node* first=t->head->left;
    if (t->count) {
        Node* p=t->head->parent;
        while (p!=t->nil) {
            destroy_subtree(t,p->right);
            Node* left=p->left;
            payload_destroy(p->payload); arch_runtime_free(p); p=left;
        }
        t->head->parent=t->nil; t->count=0;
        t->head->left=t->head; t->head->right=t->head;
    } else {
        while (first!=t->head) { Node* p=first; first=next(first); erase(t,p); }
    }
}
static void tree_initialize(Tree* t, byte allocator) {
    t->allocator[0]=allocator; t->allocator[1]=allocator; t->state[0]=0;
    Node* nil=static_cast<Node*>(arch_runtime_allocate(0x44));
    nil->parent=nullptr; nil->nil=0; nil->color=1; t->nil=nil; nil->nil=1;
    nil->left=nullptr; nil->right=nullptr;
    Node* head=node_allocate(nil,0); t->head=head;
    head->left=head; head->right=head; t->count=0;
}
extern "C" void* __thiscall archetype_root_assign(void* d,const void* s) {
    client_call(word(d,4),1); word(d,4)=word(s,4); client_call(word(d,4),0);
    if (tree(d)!=tree(s)) {
        Tree* t=tree(d); const Tree* source=tree(s);
        clear(t); t->allocator[1]=source->allocator[1];
        t->head->parent=clone(t,source->head->parent,t->head);
        t->count=source->count;
        if (t->head->parent!=t->nil) {
            t->head->left=minimum(t->head->parent); t->head->right=maximum(t->head->parent);
        } else { t->head->left=t->head; t->head->right=t->head; }
    }
    words(d,s,8,32); octet(d,0x39)=octet(s,0x39);
    words(d,s,0x24,0x34); octet(d,0x38)=octet(s,0x38); words(d,s,0x3c,0x44);
    return d;
}
static void equipment_fields(void* d,const void* s) {
    word(d,0x5c)=word(s,0x5c); octet(d,0x60)=octet(s,0x60);
    word(d,0x64)=word(s,0x64); word(d,0x68)=word(s,0x68); octet(d,0x6c)=octet(s,0x6c);
}
extern "C" void* __thiscall archetype_equipment_assign(void* d,const void* s) {
    archetype_root_assign(d,s); equipment_fields(d,s); return d;
}
extern "C" void* __thiscall archetype_attached_assign(void* d,const void* s) {
    archetype_equipment_assign(d,s); words(d,s,0x70,0x84); return d;
}
extern "C" void* __thiscall archetype_assign_0626eaf0(void* d,const void* s) {
    archetype_equipment_assign(d,s); words(d,s,0x70,0x9c); return d;
}
extern "C" void* __thiscall archetype_assign_0626dbb0(void* d,const void* s) {
    archetype_equipment_assign(d,s); word(d,0x70)=word(s,0x70); return d;
}
extern "C" void* __thiscall archetype_assign_0626e2c0(void* d,const void* s) {
    archetype_equipment_assign(d,s); words(d,s,0x70,0x98); return d;
}
static void specialized(void* d,const void* s,Word last) {
    archetype_equipment_assign(d,s); words(d,s,0x70,0x74);
    octet(d,0x78)=octet(s,0x78); octet(d,0x79)=octet(s,0x79); words(d,s,0x7c,last);
}
extern "C" void* __thiscall archetype_assign_0626f660(void* d,const void* s) {
    specialized(d,s,0xa8); octet(d,0xac)=octet(s,0xac); return d;
}
extern "C" void* __thiscall archetype_assign_0626f870(void* d,const void* s) {
    specialized(d,s,0x90); return d;
}
extern "C" void* __thiscall archetype_assign_0626fa10(void* d,const void* s) {
    specialized(d,s,0x88); return d;
}
extern "C" void arch_inherit_dispatch(void* d,void* s) {
    using Class=Word(__thiscall*)(void*);
    Word type=(*reinterpret_cast<Class**>(d))[4](d);
    if (type!=(*reinterpret_cast<Class**>(s))[4](s)) return;
    Word saved_client=word(d,4);
    if (saved_client) {
        client_call(saved_client,0);
        using Inherit=void(__thiscall*)(void*,void*);
        auto table=*reinterpret_cast<Inherit**>(saved_client);
        table[7](reinterpret_cast<void*>(saved_client),reinterpret_cast<void*>(word(s,4)));
    }
    Word nickname=word(d,8);
    switch(type) {
    case 8: case 23: case 29: archetype_equipment_assign(d,s); break;
    case 9: case 13: archetype_attached_assign(d,s); break;
    case 10: case 20: archetype_equipment_assign(d,s); words(d,s,0x70,0x78); break;
    case 11: archetype_equipment_assign(d,s); words(d,s,0x70,0x7c); break;
    case 12: archetype_equipment_assign(d,s); words(d,s,0x70,0x80); octet(d,0x84)=octet(s,0x84); word(d,0x88)=word(s,0x88); break;
    case 14: archetype_attached_assign(d,s); words(d,s,0x88,0xa4); archetype_pointer_vector_assign(static_cast<byte*>(d)+0xa8,static_cast<byte*>(s)+0xa8); break;
    case 15: archetype_attached_assign(d,s); words(d,s,0x88,0x8c); break;
    case 16: archetype_attached_assign(d,s); words(d,s,0x88,0x9c); break;
    case 17: archetype_assign_0626eaf0(d,s); words(d,s,0xa0,0xb4);
        octet(d,0xb8)=octet(s,0xb8); octet(d,0xb9)=octet(s,0xb9); octet(d,0xba)=octet(s,0xba);
        archetype_pointer_vector_assign(static_cast<byte*>(d)+0xbc,static_cast<byte*>(s)+0xbc);
        octet(d,0xcc)=octet(s,0xcc); word(d,0xd0)=word(s,0xd0); break;
    case 18: archetype_assign_0626eaf0(d,s); break;
    case 19: archetype_assign_0626eaf0(d,s); word(d,0xa0)=word(s,0xa0); break;
    case 21: archetype_equipment_assign(d,s); octet(d,0x70)=octet(s,0x70); octet(d,0x71)=octet(s,0x71); break;
    case 22: archetype_equipment_assign(d,s); words(d,s,0x70,0x74); break;
    case 24: case 25: case 26: case 27: archetype_assign_0626dbb0(d,s); break;
    case 28: archetype_assign_0626e2c0(d,s); break;
    case 31: archetype_assign_0626f660(d,s); break;
    case 32: archetype_assign_0626f870(d,s); break;
    case 33: archetype_assign_0626fa10(d,s); break;
    default: break;
    }
    word(d,8)=nickname; client_call(word(d,4),1); word(d,4)=saved_client;
}
extern "C" __declspec(noinline) void* __thiscall archetype_root_default(void* p,void* client) {
    word(p,4)=reinterpret_cast<Word>(client); word(p,8)=0; arch_cache_clear(&word(p,12));
    word(p,16)=0; word(p,20)=0; word(p,24)=0; word(p,28)=0x42c80000;
    word(p,32)=0x3f800000; word(p,36)=0; word(p,40)=0x3f800000;
    word(p,44)=0; word(p,48)=0; word(p,52)=0; octet(p,56)=0; octet(p,57)=0;
    word(p,60)=0; word(p,64)=0xffffffff; word(p,68)=0xffffffff;
    tree_initialize(tree(p),static_cast<byte>(reinterpret_cast<Word>(client)));
    vptr(p,archetype_lifetime_root_slots); return p;
}
extern "C" __declspec(noinline) void* __thiscall archetype_equipment_default(void* p,void* client) {
    archetype_root_default(p,client); word(p,0x5c)=0; octet(p,0x60)=1;
    word(p,0x64)=1; word(p,0x68)=0; octet(p,0x6c)=1;
    vptr(p,archetype_lifetime_equipment_slots); word(p,0x1c)=0x3f800000; return p;
}
extern "C" void* __thiscall archetype_attached_default(void* p,void* client) {
    archetype_equipment_default(p,client); word(p,0x70)=0; word(p,0x74)=0;
    word(p,0x78)=0; word(p,0x7c)=0; arch_cache_clear(&word(p,0x80)); word(p,0x84)=0;
    vptr(p,archetype_lifetime_attached_slots); return p;
}
extern "C" __declspec(noinline) void* __thiscall archetype_root_copy(void* p,const void* s) {
    word(p,8)=0; arch_cache_clear(&word(p,12)); word(p,36)=0;
    tree_initialize(tree(p),static_cast<byte>(reinterpret_cast<Word>(s)));
    vptr(p,archetype_lifetime_root_slots); archetype_root_assign(p,s); return p;
}
extern "C" void* __thiscall archetype_equipment_copy(void* p,const void* s) {
    archetype_root_copy(p,s); equipment_fields(p,s);
    vptr(p,archetype_lifetime_equipment_slots); return p;
}
extern "C" void* __thiscall archetype_attached_copy(void* p,const void* s) {
    archetype_root_copy(p,s); word(p,0x5c)=word(s,0x5c); octet(p,0x60)=octet(s,0x60);
    word(p,0x64)=word(s,0x64); word(p,0x68)=word(s,0x68);
    vptr(p,archetype_lifetime_equipment_slots); octet(p,0x6c)=octet(s,0x6c);
    words(p,s,0x70,0x84); vptr(p,archetype_lifetime_attached_slots); return p;
}
extern "C" void __thiscall archetype_root_destroy(void* p) {
    vptr(p,archetype_lifetime_root_slots); client_call(word(p,4),1);
    Tree* t=tree(p); clear(t);
    arch_runtime_free(t->head); Node* nil=t->nil; t->head=nullptr; t->count=0;
    arch_runtime_free(nil); t->nil=nullptr;
}
static void* deleting(void* p,Word flags,Word stride) {
    void* result=p;
    if (flags&2) {
        result=static_cast<byte*>(p)-4;
        arch_runtime_array_destroy(p,stride,word(result,0),archetype_root_destroy);
    } else archetype_root_destroy(p);
    if (flags&1) arch_runtime_free(result);
    return result;
}
extern "C" void* __thiscall archetype_root_deleting(void* p,Word f) { return deleting(p,f,0x5c); }
extern "C" void* __thiscall archetype_equipment_deleting(void* p,Word f) { return deleting(p,f,0x70); }
extern "C" void* __thiscall archetype_attached_deleting(void* p,Word f) { return deleting(p,f,0x88); }
extern "C" Word __thiscall archetype_root_class(void*) { return 0; }
extern "C" Word __thiscall archetype_equipment_class(void*) { return 6; }
extern "C" Word __thiscall archetype_attached_class(void*) { return 7; }
#define SLOT(f) reinterpret_cast<const void*>(f)
extern "C" const void* const archetype_lifetime_root_slots[6] = {SLOT(archetype_root_deleting),SLOT(archetype_root_read),nullptr,nullptr,SLOT(archetype_root_class),nullptr};
extern "C" const void* const archetype_lifetime_equipment_slots[10] = {SLOT(archetype_equipment_deleting),SLOT(archetype_equipment_read),nullptr,nullptr,SLOT(archetype_equipment_class),nullptr,nullptr,nullptr,nullptr,SLOT(archetype_equipment_is_attached)};
extern "C" const void* const archetype_lifetime_attached_slots[10] = {SLOT(archetype_attached_deleting),SLOT(archetype_attached_read),nullptr,nullptr,SLOT(archetype_attached_class),nullptr,nullptr,nullptr,nullptr,SLOT(archetype_attached_is_attached)};
