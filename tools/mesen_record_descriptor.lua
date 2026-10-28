-- Replay the actual zero-mode descriptor path with controlled descriptor
-- indices. PC injection bypasses its caller and does not establish reachability.
local cases={0x40,0x41,0x46,0x47,0x4C,0x42};local save=nil;local case=0;local active=false;local frames=0;local interrupts=0
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function setup()
 emu.write(0x2A,cases[case+1],emu.memType.nesDebug)
 local cpu=emu.getCpuState();cpu.pc=0xD71D;emu.setCpuState(cpu);interrupts=0;active=true
end
emu.addMemoryCallback(function() if active then interrupts=interrupts+1 end end,emu.callbackType.exec,0xFFC7,0xFFC7)
emu.addMemoryCallback(function()
 local m=emu.convertAddress(0xFE6C,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=0x7E6C then return end
 if not save then save=emu.createSavestate();setup();return end
 if not active then return end
 local cpu=emu.getCpuState();local ptr=r(0x53)+256*r(0x54);local mode=r(0x57);local index=r(0x2A)
 print(string.format('DESC %02X %04X %02X %02X %d',index,ptr,mode,cpu.x,interrupts))
 active=false;case=case+1
 if case==#cases then print(string.format('DONE %d',case));emu.stop(0);return end
 if not emu.loadSavestate(save) then print('LOAD_FAILED');emu.stop(1);return end
 setup()
end,emu.callbackType.exec,0xFE6C,0xFE6C)
emu.addEventCallback(function() frames=frames+1;if frames>=600 and not save then print('NO_ENTRY');emu.stop(1) end end,emu.eventType.endFrame)
