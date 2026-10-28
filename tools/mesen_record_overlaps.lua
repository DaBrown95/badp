-- Inject a descriptor and command inputs; these cases do not establish normal-play reachability.
local cases={{0xE0D6,0x18,0xFF},{0xD70F,0x1C,0x00},{0xD70F,0x1D,0x00}};local saved=nil;local case=0;local active=false;local frames=0;local nmi=0
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function w(a,v) emu.write(a,v,emu.memType.nesDebug) end
local function phys(a) local m=emu.convertAddress(a,emu.memType.nesMemory);return m and m.memType==emu.memType.nesPrgRom and m.address or -1 end
local function setup()
 local v=cases[case+1];w(0x10,5);w(0x04E5,0x21);w(0x61,v[2]);w(0x62,v[3]);w(0x53,0x34);w(0x54,0x12);w(0x03C0,0x0C);w(0x03C1,0);w(0x03C2,0x0D);w(0x03C3,1)
 for _,a in ipairs({0x0695,0x06A5,0x06B5,0x06C5,0x0625}) do w(a,0x55) end
 local cpu=emu.getCpuState();cpu.pc=v[1];cpu.x=5;emu.setCpuState(cpu);active=true;nmi=0
end
emu.addMemoryCallback(function()
 if not saved and phys(0xFE6C)==0x7E6C then saved=emu.createSavestate();setup() end
end,emu.callbackType.exec,0xFE6C,0xFE6C)
emu.addMemoryCallback(function()
 if not active then return end
 local c=emu.getCpuState();local p=r(0x53)+256*r(0x54)+c.y
 print(string.format('FETCH %d %04X %05X %02X',case,p,phys(p),r(p)))
end,emu.callbackType.exec,0xFE90,0xFE90)
emu.addMemoryCallback(function()
 if not active then return end
 local c=emu.getCpuState();print(string.format('MODE %d %02X %02X %02X',case,r(0x57),c.y,r(0x60+c.y)))
end,emu.callbackType.exec,0xF156,0xF156)
emu.addMemoryCallback(function()
 if not active then return end
 print(string.format('RESULT %d %02X %02X %02X %02X %02X %02X %02X %d',case,r(0x11),r(0x0695),r(0x06A5),r(0x06B5),r(0x06C5),r(0x53),r(0x54),nmi));active=false;case=case+1
 if case==#cases then print('DONE');emu.stop(0);return end
 if not emu.loadSavestate(saved) then print('LOAD_FAILED');emu.stop(1);return end;setup()
end,emu.callbackType.exec,0xF184,0xF184)
emu.addMemoryCallback(function() if active then nmi=nmi+1 end end,emu.callbackType.exec,0xFFC7,0xFFC7)
emu.addEventCallback(function() frames=frames+1;if frames==120 then print('TIMEOUT');emu.stop(1) end end,emu.eventType.endFrame)
