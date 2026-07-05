

import time

#HazelnuteNutBasic.py

#




class HazelnutBasicScript:
    def __init__(self):
        self.script = []
    def printScript(self):
        for command in self.script:
            print(f"{command.command}: {command.params}")



class HazelnutBasicCommand:
    def __init__(self):
        self.command = ""
        self.params = []
    def parseLine(self, line):
        splitLine = line.split(" ")
        self.command = splitLine.pop(0)

        if '"' in line:
            insideString = False
            tempString = ""
            for item in " ".join(splitLine):
                #print(item)

                if item == '"':
                    insideString = not insideString
                    if not insideString:
                        #print("TEMPSTRING:",tempString)
                        self.params.append(tempString)

                elif insideString:
                    #print(item)
                    tempString = tempString + item
                else:
                    #print("asdas")
                    if item == " ":
                        #print("TEMPSTRING:",tempString)
                        self.params.append(tempString)
                        tempString = ""
                    else:
                        tempString = tempString + item
                        #print("progress",tempString)
        else:
            for item in splitLine:
                self.params.append(item)



# inputs:
# t: string containing HazelnutBasicFileContents

def parseHazelnutBasic(t):
    script = HazelnutBasicScript()
    for line in t.split("\n"):
        if len("".join(line.split(" "))) < 1:
            continue
       # print(line)

        command = HazelnutBasicCommand()
        command.parseLine(line)
        script.script.append(command)
    return script


def createHeader(headerData):
    headerParams = {"headerSize":[0x6C,0x65, 0x6E, 0x67,0x74, 0x68, 0x00, 0x00],"compilerMinor":[0x6D,0x69, 0x6E, 0x6F,0x72, 0x76, 0x65, 0x72],"compilerMajor":[0x6D,0x61, 0x6A, 0x6F,0x72, 0x76, 0x65, 0x72], "compileTime":[0x75, 0x6E, 0x69, 0x78, 0x74, 0x69, 0x6D, 0x65]}


    # This doesnt include the header length param itself, because it is a seperate thing
    # (But it is actually part of the same thing)
    if "headerSize" not in headerData:
        headerData["headerSize"] = list(len(headerData).to_bytes(8, byteorder='big'))
    header = []


    # This sucks, but this is fine.... I think

    if "headerSize" in headerParams:
        data = headerData["headerSize"]
        header.extend(headerParams["headerSize"])
        #print("PREFIX",prefix, data)
        header.extend(data)

    for prefix in headerData:
        if prefix == "headerSize":
            continue #Header size is already handled above to ensure it is the first param
        if prefix in headerParams:
            data = headerData[prefix]
            header.extend(headerParams[prefix])
            print("PREFIX",prefix, data)
            header.extend(data)
    return header

def assembleHazelnutFile(script):

    signature = [
        # Offset 0x00000000 to 0x00000008
        0x68, 0x61, 0x7A, 0x65, 0x6C, 0x6E, 0x75, 0x74
    ]
    print(signature)

    #instructions = {"var":[0x6E, 0x65, 0x77, 0x20, 0x76, 0x61, 0x72, 0x00]}
    instructions = {"var":[0x6E, 0x77],"set$":[0x73, 0x74],"echo":[0x70,0x72]}

    compiledFile = []

    compiledFile.extend(signature)
    compiledFile.extend([0x00]*8)


    timestamp = int(time.time())


    # Yes, I made it 4 bytes so it would fail in 2038 >:3
    timestamp_bytes = list(timestamp.to_bytes(4, byteorder='big'))
    instruction_count = len(script.script)
    # Might as well put the instruction count here lol
    count_bytes = list(instruction_count.to_bytes(4, byteorder='big'))



    compiledFile.extend(createHeader( {"compilerMajor": [0x00] * 7 + [0x00], "compilerMinor": [0x00] * 7 + [0x01], "compileTime":timestamp_bytes+count_bytes}))

    currentAddress = 0

    for command in script.script:
        print(command.command)
        if command.command in instructions:
            addr_bytes = list(currentAddress.to_bytes(4, byteorder='big'))
            compiledFile.extend(addr_bytes) #TODO: Command Location (currentAddress)

            compiledFile.extend(instructions[command.command])

            #print(command.params)

            compiledFile.extend([0x00]*4) #TODO: ADDR1
            compiledFile.extend([0x00]*4) #TODO: ADDR2
            compiledFile.extend([0x00]*2) #TODO: debug data
        currentAddress += 1

    print(" ".join(f"{b:02X}" for b in compiledFile))
    return bytes(compiledFile)





def compileHazelnutBasic(t, target = "output.hazlenut", header = {}):
    script = parseHazelnutBasic(t)
    script.printScript()
    compiledFile = assembleHazelnutFile(script)
    with open(target, "wb") as f:
        f.write(compiledFile)


if __name__ == "__main__":
    headerParams = {"CompilerType":"Basic", "CompilerVersion":""}
    with open("test.hzlbsk") as f:
        compileHazelnutBasic(f.read(), header = headerParams)

