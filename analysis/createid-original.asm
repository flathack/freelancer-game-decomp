; Bounded analysis window, not a proven function extent.

/mnt/ai-models/PROJECTS/TASKS/Freelancer-Decomp/original/_FL Fresh Install-deutsch/EXE/common.dll:     file format pei-i386


Disassembly of section .text:

0630d470 <.text+0xac470>:
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
 630d4ad:	90                   	nop
 630d4ae:	90                   	nop
 630d4af:	90                   	nop
 630d4b0:	a1 a4 35 3a 06       	mov    eax,ds:0x63a35a4
 630d4b5:	a3 74 bf 3f 06       	mov    ds:0x63fbf74,eax
 630d4ba:	c3                   	ret
 630d4bb:	90                   	nop
 630d4bc:	90                   	nop
 630d4bd:	90                   	nop
 630d4be:	90                   	nop
 630d4bf:	90                   	nop
 630d4c0:	a1 a4 35 3a 06       	mov    eax,ds:0x63a35a4
 630d4c5:	a3 70 bf 3f 06       	mov    ds:0x63fbf70,eax
 630d4ca:	c3                   	ret
 630d4cb:	90                   	nop
 630d4cc:	90                   	nop
 630d4cd:	90                   	nop
 630d4ce:	90                   	nop
 630d4cf:	90                   	nop
 630d4d0:	a1 a8 35 3a 06       	mov    eax,ds:0x63a35a8
 630d4d5:	a3 6c bf 3f 06       	mov    ds:0x63fbf6c,eax
 630d4da:	c3                   	ret
 630d4db:	90                   	nop
 630d4dc:	90                   	nop
 630d4dd:	90                   	nop
 630d4de:	90                   	nop
 630d4df:	90                   	nop
 630d4e0:	8b 54 24 04          	mov    edx,DWORD PTR [esp+0x4]
 630d4e4:	8b c1                	mov    eax,ecx
 630d4e6:	66 8b 48 08          	mov    cx,WORD PTR [eax+0x8]
 630d4ea:	66 89 0a             	mov    WORD PTR [edx],cx
 630d4ed:	8a 48 0a             	mov    cl,BYTE PTR [eax+0xa]
