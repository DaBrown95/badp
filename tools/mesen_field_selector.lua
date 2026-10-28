-- Controlled probe of $3F/$24: replay one real handler entry with every $0550,x value.
local save=nil;local case=0;local active=false;local failures=0;local frames=0
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function setup()
 local cpu=emu.getCpuState();cpu.x=5;cpu.ps=(cpu.ps-(cpu.ps%2))+math.floor(case/256);emu.setCpuState(cpu)
 emu.write(0x61,0x24,emu.memType.nesDebug);emu.write(0x0555,case%256,emu.memType.nesDebug)
 emu.write(0x75,0xA5,emu.memType.nesDebug);emu.write(0x85,0xA5,emu.memType.nesDebug);active=true
end
emu.addMemoryCallback(function()
 local m=emu.convertAddress(0xDD2E,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=0x5D2E or save then return end
 save=emu.createSavestate();setup()
end,emu.callbackType.exec,0xDD2E,0xDD2E)
emu.addMemoryCallback(function()
 if not active then return end
 local m=emu.convertAddress(0xDDE7,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=0x5DE7 then failures=failures+1;return end
 local input=case%256;local expected=math.floor(input/16)+(math.floor(input/8)%2)*16
 local cpu=emu.getCpuState();local low=r(0x75);local high=r(0x85)
 if cpu.x~=5 or low~=expected or high~=0 then failures=failures+1 end
 print(string.format('FIELD %02X %d %02X %02X %02X',input,math.floor(case/256),low,high,cpu.x))
 active=false;case=case+1
 if case>=512 then print(string.format('DONE %d %d',case,failures));emu.stop(0);return end
 if not emu.loadSavestate(save) then print('LOAD_FAILED');emu.stop(1);return end
 setup()
end,emu.callbackType.exec,0xDDE7,0xDDE7)
emu.addEventCallback(function() frames=frames+1;if frames>=1800 and case==0 then print('NO_ENTRY');emu.stop(1) end end,emu.eventType.endFrame)
