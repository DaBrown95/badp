-- Controlled probe: replay one real call to the selector with all 128 nonnegative
-- selector values and both incoming carry states. No ROM bytes are changed.
local save=nil;local case=0;local active=false;local failures=0;local observed=0;local conflicts=0
local function r(a) return emu.read(a,emu.memType.nesDebug) end
emu.addMemoryCallback(function()
 local m=emu.convertAddress(0xCC95,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=0x4C95 then return end
 if not save then save=emu.createSavestate() end
 if active then failures=failures+1;return end
 local a=case%128;local carry=math.floor(case/128)
 local cpu=emu.getCpuState();cpu.a=a;cpu.ps=(cpu.ps-(cpu.ps%2))+carry;emu.setCpuState(cpu)
 active=true
end,emu.callbackType.exec,0xCC95,0xCC95)
emu.addMemoryCallback(function()
 if not active then return end
 local m=emu.convertAddress(0xCCC7,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=0x4CC7 then failures=failures+1;return end
 local a=case%128;local carry=math.floor(case/128);local value=r(0x03C2);local index=r(0x03C3)
 local expected=0x0D+math.floor((a%32)/2)*0x10;local expected_index=1+math.floor((a%32)/2)*2
 if value~=expected or index~=expected_index then failures=failures+1 end;if r(0xFFB7+index)~=value then conflicts=conflicts+1;print(string.format('CONFLICT %02X %d %02X %02X %02X',a,carry,value,index,r(0xFFB7+index))) end
 print(string.format('SELECT %02X %d %02X %02X %02X %02X',a,carry,value,index,expected,expected_index))
 observed=observed+1;active=false;case=case+1
 if case>=256 then print(string.format('DONE %d %d %d',observed,failures,conflicts));emu.stop(0);return end
 if not emu.loadSavestate(save) then failures=failures+1;print('LOAD_FAILED');emu.stop(1);return end
 local cpu=emu.getCpuState();cpu.a=case%128;cpu.ps=(cpu.ps-(cpu.ps%2))+math.floor(case/128);emu.setCpuState(cpu);active=true
end,emu.callbackType.exec,0xCCC7,0xCCC7)
