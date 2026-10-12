
original/_FL Fresh Install-deutsch/EXE/common.dll:     file format pei-i386


Disassembly of section .text:

0630d070 <.text+0xac070>:
 630d070:	a1 68 bf 3f 06       	mov    eax,ds:0x63fbf68
 630d075:	85 c0                	test   eax,eax
 630d077:	75 28                	jne    0x630d0a1
 630d079:	6a 08                	push   0x8
 630d07b:	e8 3c 4a 08 00       	call   0x6391abc
 630d080:	83 c4 04             	add    esp,0x4
 630d083:	85 c0                	test   eax,eax
 630d085:	74 13                	je     0x630d09a
 630d087:	c7 00 00 00 00 00    	mov    DWORD PTR [eax],0x0
 630d08d:	c7 40 04 01 00 00 00 	mov    DWORD PTR [eax+0x4],0x1
 630d094:	a3 68 bf 3f 06       	mov    ds:0x63fbf68,eax
 630d099:	c3                   	ret
 630d09a:	33 c0                	xor    eax,eax
 630d09c:	a3 68 bf 3f 06       	mov    ds:0x63fbf68,eax
 630d0a1:	c3                   	ret
 630d0a2:	90                   	nop
 630d0a3:	90                   	nop
 630d0a4:	90                   	nop
 630d0a5:	90                   	nop
 630d0a6:	90                   	nop
 630d0a7:	90                   	nop
 630d0a8:	90                   	nop
 630d0a9:	90                   	nop
 630d0aa:	90                   	nop
 630d0ab:	90                   	nop
 630d0ac:	90                   	nop
 630d0ad:	90                   	nop
 630d0ae:	90                   	nop
 630d0af:	90                   	nop
 630d0b0:	8b 01                	mov    eax,DWORD PTR [ecx]
 630d0b2:	85 c0                	test   eax,eax
 630d0b4:	74 07                	je     0x630d0bd
 630d0b6:	50                   	push   eax
 630d0b7:	e8 be 49 08 00       	call   0x6391a7a
 630d0bc:	59                   	pop    ecx
 630d0bd:	c3                   	ret
 630d0be:	90                   	nop
 630d0bf:	90                   	nop
 630d0c0:	56                   	push   esi
 630d0c1:	8b 35 68 bf 3f 06    	mov    esi,DWORD PTR ds:0x63fbf68
 630d0c7:	85 f6                	test   esi,esi
 630d0c9:	74 18                	je     0x630d0e3
 630d0cb:	8b 06                	mov    eax,DWORD PTR [esi]
 630d0cd:	85 c0                	test   eax,eax
 630d0cf:	74 09                	je     0x630d0da
 630d0d1:	50                   	push   eax
 630d0d2:	e8 a3 49 08 00       	call   0x6391a7a
 630d0d7:	83 c4 04             	add    esp,0x4
 630d0da:	56                   	push   esi
 630d0db:	e8 9a 49 08 00       	call   0x6391a7a
 630d0e0:	83 c4 04             	add    esp,0x4
 630d0e3:	c7 05 68 bf 3f 06 00 	mov    DWORD PTR ds:0x63fbf68,0x0
 630d0ea:	00 00 00 
 630d0ed:	5e                   	pop    esi
 630d0ee:	c3                   	ret
 630d0ef:	90                   	nop
 630d0f0:	83 ec 0c             	sub    esp,0xc
 630d0f3:	56                   	push   esi
 630d0f4:	8b f1                	mov    esi,ecx
 630d0f6:	8b 06                	mov    eax,DWORD PTR [esi]
 630d0f8:	57                   	push   edi
 630d0f9:	33 ff                	xor    edi,edi
 630d0fb:	3b c7                	cmp    eax,edi
 630d0fd:	89 74 24 10          	mov    DWORD PTR [esp+0x10],esi
 630d101:	74 0b                	je     0x630d10e
 630d103:	5f                   	pop    edi
 630d104:	b8 01 00 00 00       	mov    eax,0x1
 630d109:	5e                   	pop    esi
 630d10a:	83 c4 0c             	add    esp,0xc
 630d10d:	c3                   	ret
 630d10e:	53                   	push   ebx
 630d10f:	68 1c 04 00 00       	push   0x41c
 630d114:	e8 a3 49 08 00       	call   0x6391abc
 630d119:	8b d8                	mov    ebx,eax
 630d11b:	83 c4 04             	add    esp,0x4
 630d11e:	3b df                	cmp    ebx,edi
 630d120:	89 5c 24 10          	mov    DWORD PTR [esp+0x10],ebx
 630d124:	0f 84 24 01 00 00    	je     0x630d24e
 630d12a:	33 f6                	xor    esi,esi
 630d12c:	55                   	push   ebp
 630d12d:	c7 83 00 04 00 00 20 	mov    DWORD PTR [ebx+0x400],0x20
 630d134:	00 00 00 
 630d137:	c7 83 04 04 00 00 1e 	mov    DWORD PTR [ebx+0x404],0x1e
 630d13e:	00 00 00 
 630d141:	c7 83 08 04 00 00 05 	mov    DWORD PTR [ebx+0x408],0x8005
 630d148:	80 00 00 
 630d14b:	89 bb 0c 04 00 00    	mov    DWORD PTR [ebx+0x40c],edi
 630d151:	89 bb 10 04 00 00    	mov    DWORD PTR [ebx+0x410],edi
 630d157:	c6 83 14 04 00 00 01 	mov    BYTE PTR [ebx+0x414],0x1
 630d15e:	c6 83 15 04 00 00 01 	mov    BYTE PTR [ebx+0x415],0x1
 630d165:	89 bb 18 04 00 00    	mov    DWORD PTR [ebx+0x418],edi
 630d16b:	89 74 24 10          	mov    DWORD PTR [esp+0x10],esi
 630d16f:	eb 04                	jmp    0x630d175
 630d171:	8b 74 24 10          	mov    esi,DWORD PTR [esp+0x10]
 630d175:	8a 83 14 04 00 00    	mov    al,BYTE PTR [ebx+0x414]
 630d17b:	84 c0                	test   al,al
 630d17d:	74 26                	je     0x630d1a5
 630d17f:	8b c6                	mov    eax,esi
 630d181:	33 d2                	xor    edx,edx
 630d183:	b9 07 00 00 00       	mov    ecx,0x7
 630d188:	2b ca                	sub    ecx,edx
 630d18a:	bf 01 00 00 00       	mov    edi,0x1
 630d18f:	d3 e7                	shl    edi,cl
 630d191:	a8 01                	test   al,0x1
 630d193:	74 04                	je     0x630d199
 630d195:	0b f7                	or     esi,edi
 630d197:	eb 04                	jmp    0x630d19d
 630d199:	f7 d7                	not    edi
 630d19b:	23 f7                	and    esi,edi
 630d19d:	d1 e8                	shr    eax,1
 630d19f:	42                   	inc    edx
 630d1a0:	83 fa 08             	cmp    edx,0x8
 630d1a3:	7c de                	jl     0x630d183
 630d1a5:	8b 93 04 04 00 00    	mov    edx,DWORD PTR [ebx+0x404]
 630d1ab:	8d 4a ff             	lea    ecx,[edx-0x1]
 630d1ae:	bd 01 00 00 00       	mov    ebp,0x1
 630d1b3:	d3 e5                	shl    ebp,cl
 630d1b5:	8d 4a f8             	lea    ecx,[edx-0x8]
 630d1b8:	d3 e6                	shl    esi,cl
 630d1ba:	b8 08 00 00 00       	mov    eax,0x8
 630d1bf:	8b ce                	mov    ecx,esi
 630d1c1:	85 cd                	test   ebp,ecx
 630d1c3:	74 0c                	je     0x630d1d1
 630d1c5:	8b b3 08 04 00 00    	mov    esi,DWORD PTR [ebx+0x408]
 630d1cb:	03 c9                	add    ecx,ecx
 630d1cd:	33 ce                	xor    ecx,esi
 630d1cf:	eb 02                	jmp    0x630d1d3
 630d1d1:	d1 e1                	shl    ecx,1
 630d1d3:	48                   	dec    eax
 630d1d4:	75 eb                	jne    0x630d1c1
 630d1d6:	8a 83 14 04 00 00    	mov    al,BYTE PTR [ebx+0x414]
 630d1dc:	84 c0                	test   al,al
 630d1de:	74 35                	je     0x630d215
 630d1e0:	33 f6                	xor    esi,esi
 630d1e2:	85 d2                	test   edx,edx
 630d1e4:	8b f9                	mov    edi,ecx
 630d1e6:	8b c1                	mov    eax,ecx
 630d1e8:	7e 29                	jle    0x630d213
 630d1ea:	8d 9b 00 00 00 00    	lea    ebx,[ebx+0x0]
 630d1f0:	8b ca                	mov    ecx,edx
 630d1f2:	2b ce                	sub    ecx,esi
 630d1f4:	49                   	dec    ecx
 630d1f5:	bb 01 00 00 00       	mov    ebx,0x1
 630d1fa:	d3 e3                	shl    ebx,cl
 630d1fc:	a8 01                	test   al,0x1
 630d1fe:	74 04                	je     0x630d204
 630d200:	0b fb                	or     edi,ebx
 630d202:	eb 04                	jmp    0x630d208
 630d204:	f7 d3                	not    ebx
 630d206:	23 fb                	and    edi,ebx
 630d208:	d1 e8                	shr    eax,1
 630d20a:	46                   	inc    esi
 630d20b:	3b f2                	cmp    esi,edx
 630d20d:	7c e1                	jl     0x630d1f0
 630d20f:	8b 5c 24 14          	mov    ebx,DWORD PTR [esp+0x14]
 630d213:	8b cf                	mov    ecx,edi
 630d215:	8b 44 24 10          	mov    eax,DWORD PTR [esp+0x10]
 630d219:	8d 54 2d ff          	lea    edx,[ebp+ebp*1-0x1]
 630d21d:	83 ca 01             	or     edx,0x1
 630d220:	23 d1                	and    edx,ecx
 630d222:	89 14 83             	mov    DWORD PTR [ebx+eax*4],edx
 630d225:	40                   	inc    eax
 630d226:	3d 00 01 00 00       	cmp    eax,0x100
 630d22b:	89 44 24 10          	mov    DWORD PTR [esp+0x10],eax
 630d22f:	0f 8c 3c ff ff ff    	jl     0x630d171
 630d235:	8b 74 24 18          	mov    esi,DWORD PTR [esp+0x18]
 630d239:	8b c3                	mov    eax,ebx
 630d23b:	33 c9                	xor    ecx,ecx
 630d23d:	85 c0                	test   eax,eax
 630d23f:	5d                   	pop    ebp
 630d240:	0f 95 c1             	setne  cl
 630d243:	5b                   	pop    ebx
 630d244:	89 06                	mov    DWORD PTR [esi],eax
 630d246:	5f                   	pop    edi
 630d247:	5e                   	pop    esi
 630d248:	8b c1                	mov    eax,ecx
 630d24a:	83 c4 0c             	add    esp,0xc
 630d24d:	c3                   	ret
 630d24e:	33 c0                	xor    eax,eax
 630d250:	33 c9                	xor    ecx,ecx
 630d252:	85 c0                	test   eax,eax
 630d254:	0f 95 c1             	setne  cl
 630d257:	5b                   	pop    ebx
 630d258:	89 06                	mov    DWORD PTR [esi],eax
 630d25a:	5f                   	pop    edi
 630d25b:	5e                   	pop    esi
 630d25c:	8b c1                	mov    eax,ecx
 630d25e:	83 c4 0c             	add    esp,0xc
 630d261:	c3                   	ret
 630d262:	90                   	nop
 630d263:	90                   	nop
 630d264:	90                   	nop
 630d265:	90                   	nop
 630d266:	90                   	nop
 630d267:	90                   	nop
 630d268:	90                   	nop
 630d269:	90                   	nop
 630d26a:	90                   	nop
 630d26b:	90                   	nop
 630d26c:	90                   	nop
 630d26d:	90                   	nop
 630d26e:	90                   	nop
 630d26f:	90                   	nop
 630d270:	81 ec 00 01 00 00    	sub    esp,0x100
 630d276:	55                   	push   ebp
 630d277:	8b e9                	mov    ebp,ecx
 630d279:	83 7d 00 00          	cmp    DWORD PTR [ebp+0x0],0x0
 630d27d:	56                   	push   esi
 630d27e:	75 05                	jne    0x630d285
 630d280:	e8 6b fe ff ff       	call   0x630d0f0
 630d285:	8b b4 24 0c 01 00 00 	mov    esi,DWORD PTR [esp+0x10c]
 630d28c:	33 c0                	xor    eax,eax
 630d28e:	85 f6                	test   esi,esi
 630d290:	0f 84 02 01 00 00    	je     0x630d398
 630d296:	83 c9 ff             	or     ecx,0xffffffff
 630d299:	53                   	push   ebx
 630d29a:	57                   	push   edi
 630d29b:	8b fe                	mov    edi,esi
 630d29d:	f2 ae                	repnz scas al,BYTE PTR es:[edi]
 630d29f:	f7 d1                	not    ecx
 630d2a1:	49                   	dec    ecx
 630d2a2:	8b d9                	mov    ebx,ecx
 630d2a4:	8d 4b 01             	lea    ecx,[ebx+0x1]
 630d2a7:	8b c1                	mov    eax,ecx
 630d2a9:	c1 e9 02             	shr    ecx,0x2
 630d2ac:	8d 7c 24 10          	lea    edi,[esp+0x10]
 630d2b0:	f3 a5                	rep movs DWORD PTR es:[edi],DWORD PTR ds:[esi]
 630d2b2:	8b c8                	mov    ecx,eax
 630d2b4:	83 e1 03             	and    ecx,0x3
 630d2b7:	f3 a4                	rep movs BYTE PTR es:[edi],BYTE PTR ds:[esi]
 630d2b9:	8d 4c 24 10          	lea    ecx,[esp+0x10]
 630d2bd:	51                   	push   ecx
 630d2be:	ff 15 50 93 39 06    	call   DWORD PTR ds:0x6399350
 630d2c4:	8b 45 00             	mov    eax,DWORD PTR [ebp+0x0]
 630d2c7:	8b 90 0c 04 00 00    	mov    edx,DWORD PTR [eax+0x40c]
 630d2cd:	83 c4 04             	add    esp,0x4
 630d2d0:	85 db                	test   ebx,ebx
 630d2d2:	89 90 18 04 00 00    	mov    DWORD PTR [eax+0x418],edx
 630d2d8:	8b 7d 00             	mov    edi,DWORD PTR [ebp+0x0]
 630d2db:	8d 74 24 10          	lea    esi,[esp+0x10]
 630d2df:	7e 10                	jle    0x630d2f1
 630d2e1:	33 c0                	xor    eax,eax
 630d2e3:	8a 06                	mov    al,BYTE PTR [esi]
 630d2e5:	8b cf                	mov    ecx,edi
 630d2e7:	46                   	inc    esi
 630d2e8:	50                   	push   eax
 630d2e9:	e8 c2 00 00 00       	call   0x630d3b0
 630d2ee:	4b                   	dec    ebx
 630d2ef:	75 f0                	jne    0x630d2e1
 630d2f1:	8b 75 00             	mov    esi,DWORD PTR [ebp+0x0]
 630d2f4:	8a 86 14 04 00 00    	mov    al,BYTE PTR [esi+0x414]
 630d2fa:	84 c0                	test   al,al
 630d2fc:	75 33                	jne    0x630d331
 630d2fe:	8b 96 04 04 00 00    	mov    edx,DWORD PTR [esi+0x404]
 630d304:	8b ae 10 04 00 00    	mov    ebp,DWORD PTR [esi+0x410]
 630d30a:	8d 4a ff             	lea    ecx,[edx-0x1]
 630d30d:	b8 01 00 00 00       	mov    eax,0x1
 630d312:	d3 e0                	shl    eax,cl
 630d314:	8b 8e 18 04 00 00    	mov    ecx,DWORD PTR [esi+0x418]
 630d31a:	33 cd                	xor    ecx,ebp
 630d31c:	8d 44 00 ff          	lea    eax,[eax+eax*1-0x1]
 630d320:	83 c8 01             	or     eax,0x1
 630d323:	23 c1                	and    eax,ecx
 630d325:	8b 8e 00 04 00 00    	mov    ecx,DWORD PTR [esi+0x400]
 630d32b:	2b ca                	sub    ecx,edx
 630d32d:	d3 e0                	shl    eax,cl
 630d32f:	eb 50                	jmp    0x630d381
 630d331:	8b 8e 04 04 00 00    	mov    ecx,DWORD PTR [esi+0x404]
 630d337:	8b 9e 10 04 00 00    	mov    ebx,DWORD PTR [esi+0x410]
 630d33d:	33 c0                	xor    eax,eax
 630d33f:	49                   	dec    ecx
 630d340:	ba 01 00 00 00       	mov    edx,0x1
 630d345:	d3 e2                	shl    edx,cl
 630d347:	8b 8e 18 04 00 00    	mov    ecx,DWORD PTR [esi+0x418]
 630d34d:	33 cb                	xor    ecx,ebx
 630d34f:	8b 9e 00 04 00 00    	mov    ebx,DWORD PTR [esi+0x400]
 630d355:	8d 54 12 ff          	lea    edx,[edx+edx*1-0x1]
 630d359:	83 ca 01             	or     edx,0x1
 630d35c:	bf 08 00 00 00       	mov    edi,0x8
 630d361:	23 d1                	and    edx,ecx
 630d363:	3b df                	cmp    ebx,edi
 630d365:	72 1a                	jb     0x630d381
 630d367:	8b ea                	mov    ebp,edx
 630d369:	8b cb                	mov    ecx,ebx
 630d36b:	2b cf                	sub    ecx,edi
 630d36d:	81 e5 ff 00 00 00    	and    ebp,0xff
 630d373:	d3 e5                	shl    ebp,cl
 630d375:	83 c7 08             	add    edi,0x8
 630d378:	c1 ea 08             	shr    edx,0x8
 630d37b:	0b c5                	or     eax,ebp
 630d37d:	3b fb                	cmp    edi,ebx
 630d37f:	76 e6                	jbe    0x630d367
 630d381:	8b be 04 04 00 00    	mov    edi,DWORD PTR [esi+0x404]
 630d387:	8b 8e 00 04 00 00    	mov    ecx,DWORD PTR [esi+0x400]
 630d38d:	2b cf                	sub    ecx,edi
 630d38f:	d3 e8                	shr    eax,cl
 630d391:	5f                   	pop    edi
 630d392:	5b                   	pop    ebx
 630d393:	0d 00 00 00 80       	or     eax,0x80000000
 630d398:	5e                   	pop    esi
 630d399:	5d                   	pop    ebp
 630d39a:	81 c4 00 01 00 00    	add    esp,0x100
 630d3a0:	c2 04 00             	ret    0x4
 630d3a3:	90                   	nop
 630d3a4:	90                   	nop
 630d3a5:	90                   	nop
 630d3a6:	90                   	nop
 630d3a7:	90                   	nop
 630d3a8:	90                   	nop
 630d3a9:	90                   	nop
 630d3aa:	90                   	nop
 630d3ab:	90                   	nop
 630d3ac:	90                   	nop
 630d3ad:	90                   	nop
 630d3ae:	90                   	nop
 630d3af:	90                   	nop
 630d3b0:	8b c1                	mov    eax,ecx
 630d3b2:	8a 88 14 04 00 00    	mov    cl,BYTE PTR [eax+0x414]
 630d3b8:	84 c9                	test   cl,cl
 630d3ba:	8a 88 15 04 00 00    	mov    cl,BYTE PTR [eax+0x415]
 630d3c0:	56                   	push   esi
 630d3c1:	75 57                	jne    0x630d41a
 630d3c3:	8b 90 18 04 00 00    	mov    edx,DWORD PTR [eax+0x418]
 630d3c9:	8b f2                	mov    esi,edx
 630d3cb:	c1 e2 08             	shl    edx,0x8
 630d3ce:	84 c9                	test   cl,cl
 630d3d0:	8b 88 04 04 00 00    	mov    ecx,DWORD PTR [eax+0x404]
 630d3d6:	74 21                	je     0x630d3f9
 630d3d8:	83 e9 08             	sub    ecx,0x8
 630d3db:	d3 ee                	shr    esi,cl
 630d3dd:	0f b6 4c 24 08       	movzx  ecx,BYTE PTR [esp+0x8]
 630d3e2:	81 e6 ff 00 00 00    	and    esi,0xff
 630d3e8:	33 f1                	xor    esi,ecx
 630d3ea:	8b 0c b0             	mov    ecx,DWORD PTR [eax+esi*4]
 630d3ed:	33 ca                	xor    ecx,edx
 630d3ef:	89 88 18 04 00 00    	mov    DWORD PTR [eax+0x418],ecx
 630d3f5:	5e                   	pop    esi
 630d3f6:	c2 04 00             	ret    0x4
 630d3f9:	83 e9 08             	sub    ecx,0x8
 630d3fc:	d3 ee                	shr    esi,cl
 630d3fe:	81 e6 ff 00 00 00    	and    esi,0xff
 630d404:	8b 0c b0             	mov    ecx,DWORD PTR [eax+esi*4]
 630d407:	33 ca                	xor    ecx,edx
 630d409:	0f b6 54 24 08       	movzx  edx,BYTE PTR [esp+0x8]
 630d40e:	33 ca                	xor    ecx,edx
 630d410:	89 88 18 04 00 00    	mov    DWORD PTR [eax+0x418],ecx
 630d416:	5e                   	pop    esi
 630d417:	c2 04 00             	ret    0x4
 630d41a:	84 c9                	test   cl,cl
 630d41c:	0f b6 74 24 08       	movzx  esi,BYTE PTR [esp+0x8]
 630d421:	74 22                	je     0x630d445
 630d423:	8b 88 18 04 00 00    	mov    ecx,DWORD PTR [eax+0x418]
 630d429:	8b d1                	mov    edx,ecx
 630d42b:	81 e2 ff 00 00 00    	and    edx,0xff
 630d431:	33 d6                	xor    edx,esi
 630d433:	8b 14 90             	mov    edx,DWORD PTR [eax+edx*4]
 630d436:	c1 e9 08             	shr    ecx,0x8
 630d439:	33 d1                	xor    edx,ecx
 630d43b:	89 90 18 04 00 00    	mov    DWORD PTR [eax+0x418],edx
 630d441:	5e                   	pop    esi
 630d442:	c2 04 00             	ret    0x4
 630d445:	8b 88 04 04 00 00    	mov    ecx,DWORD PTR [eax+0x404]
 630d44b:	8b 90 18 04 00 00    	mov    edx,DWORD PTR [eax+0x418]
 630d451:	83 e9 08             	sub    ecx,0x8
 630d454:	d3 e6                	shl    esi,cl
 630d456:	8b ca                	mov    ecx,edx
 630d458:	81 e1 ff 00 00 00    	and    ecx,0xff
 630d45e:	33 34 88             	xor    esi,DWORD PTR [eax+ecx*4]
 630d461:	c1 ea 08             	shr    edx,0x8
 630d464:	33 f2                	xor    esi,edx
 630d466:	89 b0 18 04 00 00    	mov    DWORD PTR [eax+0x418],esi
 630d46c:	5e                   	pop    esi
 630d46d:	c2 04 00             	ret    0x4
 630d470:	e8 fb fb ff ff       	call   0x630d070
 630d475:	85 c0                	test   eax,eax
 630d477:	75 27                	jne    0x630d4a0
 630d479:	68 70 35 3a 06       	push   0x63a3570
 630d47e:	68 88 00 00 00       	push   0x88
 630d483:	68 44 35 3a 06       	push   0x63a3544
 630d488:	b8 01 00 10 00       	mov    eax,0x100001
 630d48d:	68 6c b4 39 06       	push   0x639b46c
 630d492:	50                   	push   eax
 630d493:	a1 28 90 39 06       	mov    eax,ds:0x6399028
 630d498:	ff 10                	call   DWORD PTR [eax]
 630d49a:	83 c4 14             	add    esp,0x14
 630d49d:	33 c0                	xor    eax,eax
 630d49f:	c3                   	ret
 630d4a0:	8b 4c 24 04          	mov    ecx,DWORD PTR [esp+0x4]
 630d4a4:	51                   	push   ecx
 630d4a5:	8b c8                	mov    ecx,eax
 630d4a7:	e8 c4 fd ff ff       	call   0x630d270
 630d4ac:	c3                   	ret
