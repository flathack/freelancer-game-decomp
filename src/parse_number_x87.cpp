#include "parse_number.hpp"
// Temporary x87 arithmetic boundary: preserves extended accumulation and the
// original binary64 rounding before an illegal-digit warning.
extern "C" __declspec(naked) double parse_number_evaluate(const NumberPlan*){
 __asm{
  push ebx
  push esi
  push edi
  sub esp,16
  mov esi,dword ptr [esp+32]
  cmp dword ptr [esi+20],2
  je character_value
  cmp dword ptr [esi+20],0
  je decimal_value
  fldz
  fldz
  mov ebx,dword ptr [esi]
  mov edi,dword ptr [esi+4]
 next_digit:
  cmp ebx,edi
  jae finished
  cmp byte ptr [ebx],'.'
  je fractional_start
  movzx eax,byte ptr [ebx]
  push eax
  call parse_number_digit
  add esp,4
  cmp eax,dword ptr [esi+12]
  jae illegal_digit
  mov dword ptr [esp],eax
  ftst
  fnstsw ax
  test ah,41h
  jne integer_digit
  fild dword ptr [esp]
  fdiv st,st(1)
  faddp st(2),st
  fimul dword ptr [esi+12]
  jmp advance
 integer_digit:
  fild dword ptr [esi+12]
  fmulp st(2),st
  fild dword ptr [esp]
  faddp st(2),st
  jmp advance
 fractional_start:
  fstp st(0)
  fild dword ptr [esi+12]
 advance:
  inc ebx
  jmp next_digit
 finished:
  fxch st(1)
  fstp st(1)
  jmp apply_sign
 illegal_digit:
  fstp st(0)
  fstp qword ptr [esp+8]
  push dword ptr [esi+8]
  call parse_number_bad_digit
  add esp,4
  fld qword ptr [esp+8]
  jmp apply_sign
 decimal_value:
  push dword ptr [esi]
  call parse_number_atof
  add esp,4
 apply_sign:
  cmp dword ptr [esi+16],0
  jge done
  fchs
  jmp done
 character_value:
  fild dword ptr [esi+24]
 done:
  add esp,16
  pop edi
  pop esi
  pop ebx
  ret
 }
}
