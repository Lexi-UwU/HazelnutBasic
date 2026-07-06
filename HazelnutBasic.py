

import time

#HazelnuteNutBasic.py

#




class HazelnutBasicScript:
    def __init__(self):
        self.script = []
        self.variables = {}
        self.lockedAddresses = []
    def printScript(self):
        for command in self.script:
            print(f"{command.command}: {command.params}")
    def newVariable(self, name):
        currrentLocation = 1
        found = False
        while not found:
            found = True
            for item in self.variables:
                if self.variables[item] == currrentLocation:
                    found = False
            if not found:
                currrentLocation = currrentLocation + 1


        self.lockedAddresses.append(currrentLocation)
        self.variables[name] = currrentLocation
        return currrentLocation


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


        if command.command in ["var"]:
            script.newVariable(command.params[0])

        print("Params",command.params)
        script.script.append(command)
    print(script.variables)
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
        #TODO: Add jump command so that it can jump over data sections
        while currentAddress in script.lockedAddresses:
            currentAddress += 1
        print(command.command)
        if command.command in instructions:
            addr_bytes = list(currentAddress.to_bytes(4, byteorder='big'))
            compiledFile.extend(addr_bytes) #TODO: Command Location (currentAddress)

            compiledFile.extend(instructions[command.command])

            #print(command.params)

            #address 1
            if command.command in ["var", "echo", "set$"]:
                compiledFile.extend(list(script.variables[command.params[0]].to_bytes(4, byteorder='big')))

            else:

                compiledFile.extend([0x00]*4)

            #address 2

            if command.command in ["set$"]:

                string_bytes = command.params[1].encode('utf-8')

                # Pad or truncate to exactly 4 bytes
                string_bytes = string_bytes[:4].ljust(4, b'\x00')

                compiledFile.extend(list(string_bytes))
            else:
                compiledFile.extend([0x00]*4)

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

