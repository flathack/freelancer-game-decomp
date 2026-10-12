// Recover unowned instruction runs only when their start has a call or data reference.
// These are inferred function boundaries, not validated reconstructions.
//@category Freelancer
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.io.*;
import java.util.*;

public class RecoverOrphanFunctions extends GhidraScript {
    @Override public void run() throws Exception {
        String[] args=getScriptArgs();
        if(args.length!=1) throw new IllegalArgumentException("Output root required");
        Path dir=Paths.get(args[0],currentProgram.getName());
        Files.createDirectories(dir);
        Listing listing=currentProgram.getListing();
        AddressSet executable=new AddressSet();
        for(MemoryBlock b:currentProgram.getMemory().getBlocks())
            if(b.isExecute() && b.isInitialized()) executable.add(b.getStart(),b.getEnd());
        List<Address> candidates=new ArrayList<>();
        Address previousEnd=null;
        InstructionIterator iter=listing.getInstructions(executable,true);
        while(iter.hasNext()) {
            monitor.checkCancelled();
            Instruction i=iter.next();
            if(listing.getFunctionContaining(i.getAddress())!=null) { previousEnd=null; continue; }
            boolean start=previousEnd==null || !previousEnd.equals(i.getMinAddress().previous());
            previousEnd=i.getMaxAddress();
            if(start) candidates.add(i.getAddress());
        }
        int created=0,skipped=0;
        try(BufferedWriter out=Files.newBufferedWriter(dir.resolve("recovered-functions.tsv"),StandardCharsets.UTF_8)) {
            out.write("address\treference_evidence\tresult\n");
            for(Address address:candidates) {
                monitor.checkCancelled();
                if(listing.getFunctionContaining(address)!=null) continue;
                boolean call=false,data=false;
                for(Reference r:getReferencesTo(address)) {
                    call |= r.getReferenceType().isCall();
                    data |= r.getReferenceType().isData();
                }
                if(!call && !data) { skipped++; continue; }
                String evidence=call ? "call_target" : "data_pointer_to_instruction_run";
                Function f=createFunction(address,null);
                out.write(address+"\t"+evidence+"\t"+(f==null ? "creation_failed" : "inferred_created")+"\n");
                if(f!=null) created++;
            }
        }
        println("ORPHAN_RECOVERY "+currentProgram.getName()+" created="+created+" skipped_without_reference="+skipped);
    }
}
