-- Inject wrapper inputs. At the computed target, substitute a RAM mapper
-- write and RTS, checking continuation without running either helper body.
-- These cases do not establish ordinary script or mapper-state reachability.
local cases={{CALL_CASES}}
local saved=nil;local index=0;local phase=0;local frames=0;local nmi=0;local done=false
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function w(a,v) emu.write(a,v,emu.memType.nesDebug) end
local function phys(a)
 local m=emu.convertAddress(a,emu.memType.nesMemory)
 return m and m.memType==emu.memType.nesPrgRom and m.address or -1
end
local function setup()
 phase=0;nmi=0
 local item=cases[index+1];local operand=item[4];local stack=item[5]
 w(0x03C0,0x0C+item[2]);w(0x03C1,item[2]);w(0x03C2,0x0C+item[3]);w(0x03C3,item[3])
 w(0x61,operand%256);w(0x62,math.floor(operand/256));w(0x53,0x34);w(0x54,0x12)
 -- Synthetic LDA #value / LDY #index / STA $FFB7,Y / RTS. The helper
 -- returns in either bank, independently of the computed entry mapping.
 local stub={0xA9,0x0C+item[6],0xA0,item[6],0x99,0xB7,0xFF,0x60}
 for offset,value in ipairs(stub) do w(0x01FF+offset,value) end
 w(0x100+stack+1,0xFF);w(0x100+stack+2,0x02)
 emu.write(0xFFB7+item[1],0x0C+item[1],emu.memType.nesMemory)
 local c=emu.getCpuState();c.pc=0xFD88;c.sp=stack;emu.setCpuState(c)
 print(string.format('ENTRY %d %05X %02X',index,phys(0xFD88),emu.getCpuState().sp))
 phase=1
end
emu.addMemoryCallback(function()
 if saved or done or phys(0xFE6C)~=0x7E6C then return end
 saved=emu.createSavestate();setup()
end,emu.callbackType.exec,0xFE6C,0xFE6C)
emu.addMemoryCallback(function(a,v)
 if phase>0 then print(string.format('WRITE %d %d %04X %02X %02X %05X',index,phase,a,v,r(a),phys(a))) end
end,emu.callbackType.write,0xFFB7,0xFFB8)
local function target()
 if phase~=1 then return end
 local c=emu.getCpuState();local p=c.pc
 local operand=cases[index+1][4];local wanted=((operand|0x8000)+1)&0xFFFF
 if p~=wanted then return end
 print(string.format('TARGET %d %04X %d %02X %02X %02X %02X %02X %04X',index,p,phys(p),c.sp,
  r(0x100+c.sp+1),r(0x100+c.sp+2),r(0x100+c.sp+3),r(0x100+c.sp+4),r(0x53)+256*r(0x54)))
 phase=2;c.pc=0x0200;emu.setCpuState(c)
end
for _,address in ipairs({0xB51C,0xBEEA,0}) do emu.addMemoryCallback(target,emu.callbackType.exec,address,address) end
emu.addMemoryCallback(function()
 if phase~=2 then return end
 local c=emu.getCpuState()
 print(string.format('CONTINUE %d %05X %02X',index,phys(0xFD99),c.sp));phase=3
end,emu.callbackType.exec,0xFD99,0xFD99)
emu.addMemoryCallback(function()
 if phase~=3 then return end
 local c=emu.getCpuState()
 print(string.format('RETURN %d %05X %02X %04X %04X %d',index,phys(0xFD88),c.sp,
  r(0x61)+256*r(0x62),r(0x53)+256*r(0x54),nmi))
 phase=0;index=index+1
 if index==#cases then done=true;print(string.format('DONE %d',index));emu.stop(0);return end
 if not emu.loadSavestate(saved) then done=true;print('LOAD_FAILED');emu.stop(1);return end
 setup()
end,emu.callbackType.exec,0x0300,0x0300)
emu.addMemoryCallback(function() if phase>0 then nmi=nmi+1 end end,emu.callbackType.exec,0xFFC7,0xFFC7)
emu.addEventCallback(function() frames=frames+1;if frames>=120 and not done then done=true;print('TIMEOUT');emu.stop(1) end end,emu.eventType.endFrame)
