-- Replay the real shared fetch helper with synthetic zero-page contents.
-- Cases 0 and 1 differ only at RAM $04; case 2 uses the secondary selector;
-- case 3 starts five bytes before CPU-address wrap. No gameplay route is used.
local save=nil;local case=0;local active=false;local reads=0;local failures=0;local interrupts=0;local frames=0
local bases={0xFFFF,0xFFFF,0x7FFF,0xFFFB}
local function r(a) return emu.read(a,emu.memType.nesDebug) end
local function setup()
 local base=bases[case+1];local cpu=emu.getCpuState();cpu.x=10;emu.setCpuState(cpu)
 for i=0,8 do emu.write(i,0x30+i+((case==1 and i==4) and 0x40 or 0),emu.memType.nesDebug) end
 emu.write(0x53,base%256,emu.memType.nesDebug);emu.write(0x54,math.floor(base/256),emu.memType.nesDebug)
 emu.write(0x03C0,0x0C,emu.memType.nesDebug);emu.write(0x03C1,0,emu.memType.nesDebug)
 emu.write(0x03C2,0x0D,emu.memType.nesDebug);emu.write(0x03C3,1,emu.memType.nesDebug)
 reads=0;interrupts=0;active=true
end
emu.addMemoryCallback(function()
 if save then return end
 local m=emu.convertAddress(0xFE6C,emu.memType.nesMemory)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=0x7E6C then return end
 save=emu.createSavestate();setup()
end,emu.callbackType.exec,0xFE6C,0xFE6C)
emu.addMemoryCallback(function()
 if active then interrupts=interrupts+1 end
end,emu.callbackType.exec,0xFFC7,0xFFC7)
emu.addMemoryCallback(function()
 if not active then return end
 local cpu=emu.getCpuState();local y=cpu.y;local base=bases[case+1];local addr=((base|0x8000)+y)%0x10000
 local m=emu.convertAddress(addr,emu.memType.nesMemory);local actual=r(0x60+y);local expected=r(addr)
 local p=(m and m.address) or -1;local mt=m and m.memType or -1;local expectedBank=(case==2) and 1 or 0
 local expectType=addr>=0x8000 and emu.memType.nesPrgRom or emu.memType.nesInternalRam
 local expectPhys=addr>=0x8000 and (expectedBank*0x8000+addr-0x8000) or addr
 if y~=reads or actual~=expected or mt~=expectType or p~=expectPhys then failures=failures+1 end
 local kind=(mt==emu.memType.nesPrgRom) and 'prg' or ((mt==emu.memType.nesInternalRam) and 'ram' or 'other')
 print(string.format('COPY %d %d %04X %s %05X %02X',case,y,addr,kind,p,actual));reads=reads+1
end,emu.callbackType.exec,0xFE95,0xFE95)
local function finish()
 if not active then return end
 local cpu=emu.getCpuState();local m=emu.convertAddress(0x8000,emu.memType.nesMemory);local wantedY=(case==2) and 0 or 10
 if reads~=10 or interrupts~=0 or cpu.x~=0 or cpu.y~=wantedY or r(0xFE)~=10 or r(0x54)~=math.floor(bases[case+1]/256) or not m or m.address~=0 then failures=failures+1 end
 print(string.format('CASE %d %d %d %02X %02X %02X %d',case,reads,interrupts,cpu.x,cpu.y,r(0x54),m and m.address or -1))
 active=false;case=case+1
 if case==#bases then print(string.format('DONE %d %d',case,failures));emu.stop(failures==0 and 0 or 1);return end
 if not emu.loadSavestate(save) then print('LOAD_FAILED');emu.stop(1);return end
 setup()
end
emu.addMemoryCallback(function() if case~=2 then finish() end end,emu.callbackType.exec,0xFEA8,0xFEA8)
emu.addMemoryCallback(function() if case==2 and reads==10 then finish() end end,emu.callbackType.exec,0xFFB6,0xFFB6)
emu.addEventCallback(function()frames=frames+1;if frames>=600 and not save then print('NO_ENTRY');emu.stop(1) end end,emu.eventType.endFrame)
