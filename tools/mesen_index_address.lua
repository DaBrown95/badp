-- Controlled probe: replay opcode $44 with all low-byte inputs and carry states.
local save=nil;local case=0;local active=false;local failures=0;local frames=0
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function setup()
 local cpu=emu.getCpuState();cpu.x=5;cpu.ps=(cpu.ps-(cpu.ps%2))+math.floor(case/256);emu.setCpuState(cpu)
 emu.write(0x53,0x35,emu.memType.nesDebug);emu.write(0x54,0x74,emu.memType.nesDebug)
 emu.write(0x75,case%256,emu.memType.nesDebug);active=true
end
emu.addMemoryCallback(function()
 local m=emu.convertAddress(0xDEB3,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=0x5EB3 or save then return end
 save=emu.createSavestate();setup()
end,emu.callbackType.exec,0xDEB3,0xDEB3)
emu.addMemoryCallback(function()
 if not active then return end
 local m=emu.convertAddress(0xDEBF,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=0x5EBF then failures=failures+1;return end
 local input=case%256;local expected=0x7435+((input*2)%256);local address=r(0x53)+256*r(0x54)
 if address~=expected then failures=failures+1 end
 print(string.format('INDEX %02X %d %04X',input,math.floor(case/256),address))
 active=false;case=case+1
 if case>=512 then print(string.format('DONE %d %d',case,failures));emu.stop(0);return end
 if not emu.loadSavestate(save) then print('LOAD_FAILED');emu.stop(1);return end
 setup()
end,emu.callbackType.exec,0xDEBF,0xDEBF)
emu.addEventCallback(function() frames=frames+1;if frames>=1800 and case==0 then print('NO_ENTRY');emu.stop(1) end end,emu.eventType.endFrame)
