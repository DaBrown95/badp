-- Inject reviewed record pointers to check fetches and sentinel-selected reads.
-- This does not establish that every descriptor/event context occurs in play.
local cases={{RECORD_CASES}}
local scriptLow={{SCRIPT_LOW_BASE}};local scriptHigh={{SCRIPT_HIGH_BASE}}
local saved=nil;local case=0;local active=false;local frames=0;local nmi=0;local done=false
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function w(a,v) emu.write(a,v,emu.memType.nesDebug) end
local function phys(a) local m=emu.convertAddress(a,emu.memType.nesMemory);return m and m.memType==emu.memType.nesPrgRom and m.address or -1 end
local function setup()
 local p=cases[case+1];w(0xFE,p%256);w(0xFF,math.floor(p/256));w(0x57,0);w(0x10,5);w(0x11,0x55)
 w(0x53,0x34);w(0x54,0x12);w(scriptLow+5,0x34);w(scriptHigh+5,0x12)
 w(0x03C0,0x0C);w(0x03C1,0);w(0x03C2,0x0D);w(0x03C3,1)
 -- STA absolute,Y reads the destination before storing each fetched byte.
 -- Seed all ten old bytes so those copy-phase bus reads have known values.
 for a=0x60,0x69 do w(a,0xA5) end
 for _,a in ipairs({0x0695,0x06A5,0x06B5,0x06C5,0x0625}) do w(a,0x55) end
 local c=emu.getCpuState();c.pc=0xF10C;c.x=5;emu.setCpuState(c);active=true;nmi=0
end
emu.addMemoryCallback(function()
 if saved or done or phys(0xFE6C)~=0x7E6C then return end
 saved=emu.createSavestate();setup()
end,emu.callbackType.exec,0xFE6C,0xFE6C)
emu.addMemoryCallback(function()
 if not active then return end
 local c=emu.getCpuState();local p=r(0x53)+256*r(0x54)+c.y
 print(string.format('FETCH %d %04X %05X %02X',case,p,phys(p),r(p)))
end,emu.callbackType.exec,0xFE90,0xFE90)
emu.addMemoryCallback(function(a,v)
 if active then print(string.format('READ %d %d %02X',case,a-0x60,v)) end
end,emu.callbackType.read,0x60,0x69)
emu.addMemoryCallback(function()
 if active then print('UNEXPECTED_FIELDS');done=true;emu.stop(1) end
end,emu.callbackType.exec,0xF14E,0xF14E)
emu.addMemoryCallback(function()
 if not active then return end
 print(string.format('RESULT %d %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %d',case,r(0x11),r(0x0695),r(0x06A5),r(0x06B5),r(0x06C5),r(0x0625),r(0x53),r(0x54),r(scriptLow+5),r(scriptHigh+5),nmi))
 active=false;case=case+1
 if case==#cases then done=true;print(string.format('DONE %d',case));emu.stop(0);return end
 if not emu.loadSavestate(saved) then done=true;print('LOAD_FAILED');emu.stop(1);return end
 setup()
end,emu.callbackType.exec,0xF296,0xF296)
emu.addMemoryCallback(function() if active then nmi=nmi+1 end end,emu.callbackType.exec,0xFFC7,0xFFC7)
emu.addEventCallback(function() frames=frames+1;if frames>=120 and not done then done=true;print('TIMEOUT');emu.stop(1) end end,emu.eventType.endFrame)
