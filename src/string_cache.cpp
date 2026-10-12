#include "string_cache.hpp"
char StringCacheArena[0x180000];
unsigned int StringCacheFront=1,StringCacheBack=0x180000,StringCacheInternedCount=1,StringCachePrivateCount=0;
StringCacheTree* StringCacheIndex=nullptr;
static void initialize_index() {
    if(StringCacheIndex) return;
    StringCacheTree* t=static_cast<StringCacheTree*>(stringcache_runtime_allocate(sizeof(StringCacheTree)));
    if(!t) { StringCacheIndex=nullptr;return; }
    t->multi=0;
    t->nil=static_cast<StringCacheNode*>(stringcache_runtime_allocate(sizeof(StringCacheNode)));
    t->nil->parent=nullptr;t->nil->left=nullptr;t->nil->right=nullptr;t->nil->color=1;t->nil->is_nil=1;
    t->head=static_cast<StringCacheNode*>(stringcache_runtime_allocate(sizeof(StringCacheNode)));
    t->head->parent=t->nil;t->head->left=t->head;t->head->right=t->head;t->head->color=0;t->head->is_nil=0;
    t->size=0;StringCacheIndex=t;
}
static StringCacheNode* find(const char* text) {
    StringCacheTree* t=StringCacheIndex;
    StringCacheNode* candidate=t->head;
    for(StringCacheNode* n=t->head->parent;n!=t->nil;) {
        if(stringcache_runtime_compare(n->key,text)<0) n=n->right;
        else {candidate=n;n=n->left;}
    }
    if(candidate!=t->head && stringcache_runtime_compare(text,candidate->key)>=0) return candidate;
    return t->head;
}
static void rotate_left(StringCacheNode* x) {
    StringCacheTree* t=StringCacheIndex;StringCacheNode* y=x->right;
    x->right=y->left;if(y->left!=t->nil)y->left->parent=x;
    y->parent=x->parent;
    if(x==t->head->parent)t->head->parent=y;
    else if(x==x->parent->left)x->parent->left=y;
    else x->parent->right=y;
    y->left=x;x->parent=y;
}
static void rotate_right(StringCacheNode* x) {
    StringCacheTree* t=StringCacheIndex;StringCacheNode* y=x->left;
    x->left=y->right;if(y->right!=t->nil)y->right->parent=x;
    y->parent=x->parent;
    if(x==t->head->parent)t->head->parent=y;
    else if(x==x->parent->right)x->parent->right=y;
    else x->parent->left=y;
    y->right=x;x->parent=y;
}
static StringCacheNode* insert(char* text) {
    StringCacheTree* t=StringCacheIndex;StringCacheNode* parent=t->head;StringCacheNode* x=t->head->parent;bool left=true;
    while(x!=t->nil) {parent=x;left=stringcache_runtime_compare(text,x->key)<0;x=left?x->left:x->right;}
    StringCacheNode* z=static_cast<StringCacheNode*>(stringcache_runtime_allocate(sizeof(StringCacheNode)));
    z->left=z->right=t->nil;z->parent=parent;z->key=text;z->value=nullptr;z->color=0;z->is_nil=0;++t->size;
    if(parent==t->head){t->head->parent=z;t->head->left=z;t->head->right=z;}
    else if(left){parent->left=z;if(parent==t->head->left)t->head->left=z;}
    else {parent->right=z;if(parent==t->head->right)t->head->right=z;}
    StringCacheNode* inserted=z;
    while(z!=t->head->parent && z->parent->color==0) {
        StringCacheNode* p=z->parent;StringCacheNode* g=p->parent;
        if(p==g->left) {
            StringCacheNode* uncle=g->right;
            if(uncle->color==0){p->color=1;uncle->color=1;g->color=0;z=g;}
            else{if(z==p->right){z=p;rotate_left(z);}z->parent->color=1;z->parent->parent->color=0;rotate_right(z->parent->parent);}
        } else {
            StringCacheNode* uncle=g->left;
            if(uncle->color==0){p->color=1;uncle->color=1;g->color=0;z=g;}
            else{if(z==p->left){z=p;rotate_right(z);}z->parent->color=1;z->parent->parent->color=0;rotate_left(z->parent->parent);}
        }
    }
    t->head->parent->color=1;return inserted;
}
char* StringAlloc(const char* text,bool private_copy) {
    if(!text || !*text)return StringCacheArena;
    if(!private_copy){initialize_index();StringCacheNode* n=find(text);if(n!=StringCacheIndex->head && n->value)return n->value;}
    unsigned int length=0;while(text[length])++length;
    unsigned int bytes=length+1;
    if(bytes>StringCacheBack-StringCacheFront){stringcache_runtime_overflow(private_copy?0xb9:0xa9);return StringCacheArena;}
    char* destination=private_copy?StringCacheArena+StringCacheBack-bytes:StringCacheArena+StringCacheFront;
    for(unsigned int i=0;i<bytes;++i)destination[i]=text[i];
    if(private_copy){StringCacheBack-=bytes;++StringCachePrivateCount;}
    else{insert(destination)->value=destination;StringCacheFront+=bytes;++StringCacheInternedCount;}
    return destination;
}
void CacheString::clear(){value=StringCacheArena;}
static void erase_subtree(StringCacheNode* node) {
    StringCacheNode* nil=StringCacheIndex->nil;
    while(node!=nil) {
        erase_subtree(node->right);
        StringCacheNode* left=node->left;
        stringcache_runtime_free(node);
        node=left;
    }
}
void StringShutdown() {
    StringCacheTree* tree=StringCacheIndex;
    if(!tree)return;
    // Match the observed right-subtree, current-node, then left-chain order.
    if(tree->size) {
        erase_subtree(tree->head->parent);
        tree->head->parent=tree->nil;
        tree->size=0;
        tree->head->left=tree->head;
        tree->head->right=tree->head;
    }
    stringcache_runtime_free(tree->head);
    tree->head=nullptr;tree->size=0;
    stringcache_runtime_free(tree->nil);
    tree->nil=nullptr;
    stringcache_runtime_free(tree);
    StringCacheIndex=nullptr;
    // The original does not rewind the arena or reset allocation counters.
}
