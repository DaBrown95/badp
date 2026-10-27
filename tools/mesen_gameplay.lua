-- The runner supplies SCENARIO as 0 (Noah), 1 (Moses), or 2 (David).
-- Inputs and snapshots are deterministic candidates for the pinned v1.5 ROM.
-- Mapper callbacks record the CPU write and the byte currently mapped by Mesen.
local frames=0
local writes=0
local mismatch=0
local unmapped=0
local banks={[0]=false,[1]=false}
local nmis=0
local apu_writes=0
local dma_writes=0
local fetch_probes=0
local record_probes=0
local script_targets={0x3D21,0x3D22,0x5CFE,0x5D00,0x5D01,0x5D04,0x5D06,0x5D08,0x5D0A}
local record_targets={0x5A40,0x6D71,0x6E65,0x6E7F,0x6ECD,0x6EE5,0x6EFD}
local script_hits={}
local record_hits={}
for _,address in ipairs(script_targets) do script_hits[address]=0 end
for _,address in ipairs(record_targets) do record_hits[address]=0 end
local function hex(s)
 local out={};for i=1,#s do out[i]=string.format('%02x',string.byte(s,i)) end
 return table.concat(out)
end
emu.addMemoryCallback(function(addr,value)
 local m=emu.convertAddress(addr,emu.memType.nesMemory)
 local phys=(m and m.memType==emu.memType.nesPrgRom) and m.address or -1
 local rom=(phys>=0) and emu.read(phys,emu.memType.nesPrgRom) or -1
 writes=writes+1
 if phys<0 then unmapped=unmapped+1 elseif value~=rom then mismatch=mismatch+1 end
 if phys>=0 and phys<0x10000 then banks[math.floor(phys/0x8000)]=true end
 print(string.format('BADP_WRITE %d %04X %02X %d %d',frames,addr,value,phys,rom))
end,emu.callbackType.write,0x8000,0xffff)
local function audio_write(addr,value)
 apu_writes=apu_writes+1
 print(string.format('BADP_APU %d %04X %02X',frames,addr,value))
end
emu.addMemoryCallback(audio_write,emu.callbackType.write,0x4000,0x4013)
emu.addMemoryCallback(audio_write,emu.callbackType.write,0x4015,0x4015)
emu.addMemoryCallback(function(addr,value)
 dma_writes=dma_writes+1
 print(string.format('BADP_DMA %d %04X %02X',frames,addr,value))
end,emu.callbackType.write,0x4014,0x4014)
emu.addEventCallback(function() nmis=nmis+1 end,emu.eventType.nmi)
-- Check only the bank-0 interpreter and record-loader entry points. Debug
-- reads have no side effects; candidate identities are encoded pointers.
emu.addMemoryCallback(function()
 local mapped=emu.convertAddress(0xD54E,emu.memType.nesMemory)
 if mapped and mapped.memType==emu.memType.nesPrgRom and mapped.address==0x554E then
  fetch_probes=fetch_probes+1
  local pointer=emu.read(0x53,emu.memType.nesDebug)+256*emu.read(0x54,emu.memType.nesDebug)
  if script_hits[pointer] then script_hits[pointer]=script_hits[pointer]+1 end
 end
end,emu.callbackType.exec,0xD54E,0xD54E)
emu.addMemoryCallback(function()
 local mapped=emu.convertAddress(0xF10C,emu.memType.nesMemory)
 if mapped and mapped.memType==emu.memType.nesPrgRom and mapped.address==0x710C then
  record_probes=record_probes+1
  local pointer=emu.read(0xFE,emu.memType.nesDebug)+256*emu.read(0xFF,emu.memType.nesDebug)
  if record_hits[pointer] then record_hits[pointer]=record_hits[pointer]+1 end
 end
end,emu.callbackType.exec,0xF10C,0xF10C)
emu.addEventCallback(function()
 local move=frames>=180 and frames<185
 local start=(frames>=300 and frames<305) or (frames>=900 and frames<905)
 local right=frames>=1450 and frames<1750
 local jump=frames>=1500 and frames<1510
 local pickup=false
 if SCENARIO==1 then
  -- Lift Moses, cross the first water gap and continue through the level.
  right=(frames>=1450 and frames<1481) or (frames>=1508 and frames<2800)
  pickup=frames>=1481 and frames<1491
  jump=(frames>=1508 and frames<2000 and ((frames-1508)%220)<28)
       or (frames>=2046 and frames<2074)
       or (frames>=2250 and ((frames-2250)%190)<28)
 end
 emu.setInput({up=move and SCENARIO==0,down=move and SCENARIO==2,left=false,right=right,start=start,select=false,a=jump,b=pickup},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frames=frames+1
 if frames==240 or frames==650 or frames==1200 or frames==1400 or frames==1496 or frames==1511 or frames==1550 or frames==1700 or frames==1800 or frames==2100 or frames==2150 or frames==2300 or frames==2400 or frames==2600 or frames==2800 then
  local state=emu.getState()
  local p=emu.convertAddress(0x8000,emu.memType.nesMemory)
  print(string.format('BADP_FRAME %d %d %d %d %d %d %d %d %s',frames,emu.read(0,emu.memType.nesDebug),emu.read(1,emu.memType.nesDebug),emu.read(0x03ee,emu.memType.nesDebug)+256*emu.read(0x03ef,emu.memType.nesDebug),emu.read(0x03f0,emu.memType.nesDebug)+256*emu.read(0x03f1,emu.memType.nesDebug),p.address,state['cpu.cycleCount'],nmis,hex(emu.takeScreenshot())))
 end
 if frames==1400 or frames==1496 or frames==1511 or frames==1550 or frames==1700 or frames==1800 or frames==2100 or frames==2150 or frames==2300 or frames==2400 or frames==2600 or frames==2800 then
  print(string.format('BADP_SLOT %d %d %d %d %d %d %d %d',frames,
   emu.read(0x04E1,emu.memType.nesDebug),emu.read(0x04E2,emu.memType.nesDebug),
   emu.read(0x06D2,emu.memType.nesDebug),emu.read(0x0582,emu.memType.nesDebug),
   emu.read(0x0592,emu.memType.nesDebug),emu.read(0x0581,emu.memType.nesDebug),
   emu.read(0x0591,emu.memType.nesDebug)))
 end
 if frames==2800 then
  print(string.format('BADP_SUMMARY %d %d %d %d %d %d %d %d',writes,mismatch,unmapped,banks[0] and 1 or 0,banks[1] and 1 or 0,nmis,apu_writes,dma_writes))
  print(string.format('BADP_PROBE %d %d',fetch_probes,record_probes))
  for _,address in ipairs(script_targets) do print(string.format('BADP_TARGET script %04X %d',address,script_hits[address])) end
  for _,address in ipairs(record_targets) do print(string.format('BADP_TARGET record %04X %d',address,record_hits[address])) end
  emu.stop(0)
 end
end,emu.eventType.endFrame)
