// Export recovered types, executable instructions, and not-yet-classified bytes.
//@category Freelancer
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.data.DataTypeWriter;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.io.*;

public class ExportContext extends GhidraScript {
    private String clean(String s) { return s.replace('\t',' ').replace('\n',' ').replace('\r',' '); }
    @Override public void run() throws Exception {
        String[] args=getScriptArgs();
        if (args.length!=1) throw new IllegalArgumentException("Output root required");
        Path dir=Paths.get(args[0],currentProgram.getName());
        Files.createDirectories(dir);
        try (BufferedWriter types=Files.newBufferedWriter(dir.resolve("recovered-types.h"),StandardCharsets.UTF_8)) {
            types.write("/* Recovered Ghidra types; layouts and names require verification. */\n");
            new DataTypeWriter(currentProgram.getDataTypeManager(),types).write(currentProgram.getDataTypeManager(),monitor);
        }
        AddressSet executable=new AddressSet();
        for (MemoryBlock b:currentProgram.getMemory().getBlocks())
            if (b.isExecute() && b.isInitialized()) executable.add(b.getStart(),b.getEnd());
        AddressSet remaining=new AddressSet(executable);
        long instructions=0,instructionBytes=0,dataBytes=0;
        Listing listing=currentProgram.getListing();
        try (BufferedWriter out=Files.newBufferedWriter(dir.resolve("instructions.tsv"),StandardCharsets.UTF_8)) {
            out.write("address\tbytes\tfunction\tinstruction\n");
            InstructionIterator iter=listing.getInstructions(executable,true);
            while(iter.hasNext()) {
                monitor.checkCancelled();
                Instruction i=iter.next();
                Function f=listing.getFunctionContaining(i.getAddress());
                StringBuilder bytes=new StringBuilder();
                for(byte b:i.getBytes()) bytes.append(String.format("%02x",b&255));
                out.write(i.getAddress()+"\t"+bytes+"\t"+(f==null ? "" : f.getEntryPoint())+"\t"+clean(i.toString())+"\n");
                remaining.delete(i.getMinAddress(),i.getMaxAddress());
                instructions++; instructionBytes+=i.getLength();
            }
        }
        try (BufferedWriter out=Files.newBufferedWriter(dir.resolve("defined-data.tsv"),StandardCharsets.UTF_8)) {
            out.write("address\tlength\ttype\tvalue\n");
            DataIterator iter=listing.getDefinedData(true);
            while(iter.hasNext()) {
                monitor.checkCancelled();
                Data d=iter.next();
                out.write(d.getAddress()+"\t"+d.getLength()+"\t"+clean(d.getDataType().getPathName())+"\t"+clean(d.getDefaultValueRepresentation())+"\n");
                AddressSet intersection=executable.intersectRange(d.getMinAddress(),d.getMaxAddress());
                dataBytes+=intersection.getNumAddresses();
                remaining.delete(d.getMinAddress(),d.getMaxAddress());
            }
        }
        try (BufferedWriter out=Files.newBufferedWriter(dir.resolve("unclassified-executable.tsv"),StandardCharsets.UTF_8)) {
            out.write("start\tend\tlength\tfirst_64_bytes\n");
            AddressRangeIterator iter=remaining.getAddressRanges();
            while(iter.hasNext()) {
                monitor.checkCancelled();
                AddressRange r=iter.next();
                int count=(int)Math.min(64,r.getLength());
                byte[] buffer=new byte[count];
                currentProgram.getMemory().getBytes(r.getMinAddress(),buffer);
                StringBuilder bytes=new StringBuilder();
                for(byte b:buffer) bytes.append(String.format("%02x",b&255));
                out.write(r.getMinAddress()+"\t"+r.getMaxAddress()+"\t"+r.getLength()+"\t"+bytes+"\n");
            }
        }
        Files.writeString(dir.resolve("context-summary.json"),"{\n  \"executable_mapped_bytes\": "+executable.getNumAddresses()+",\n  \"instruction_count\": "+instructions+",\n  \"instruction_bytes\": "+instructionBytes+",\n  \"defined_data_bytes_in_executable\": "+dataBytes+",\n  \"unclassified_executable_bytes\": "+remaining.getNumAddresses()+"\n}\n");
        println("CONTEXT_DONE "+currentProgram.getName()+" unclassified="+remaining.getNumAddresses());
    }
}
