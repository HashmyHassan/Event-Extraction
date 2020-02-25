import ijson
import sys
import csv

def parseJson(input_path, output_path, date_file,url,newsid):
    json_f = open(input_path)
    data_objects = ijson.items(json_f,"item")

    date_inp = open(date_file, 'w')
    url_inp = open(url, 'w')
    id_inp = open(newsid, 'w')
    writer = csv.writer(date_inp)
    writer1 = csv.writer(url_inp)
    writer2 = csv.writer(id_inp)
    count = 1
    #write content of each json object in a different file
    for data in data_objects:
        description = data["whole_content"]
        brief = data["content"]
        if not description and not brief:
            continue
        data_to_write = ""
        if not description:
            data_to_write = brief
        else:
            data_to_write = description

        # file_name = data["source"] + "_" + data["_id"]["$oid"] + "_input.txt"

        if not data["title"] or not data_to_write or not data["publishAt"]["$date"]:
            continue
        list_string  = data["title"][:100].split()
        title = '_'.join(list_string)
        file_name = str(count) + "_" + title.replace('/','_') + "_" + data["publishAt"]["$date"][:10] + ".txt"
        f = open(output_path + "/" + file_name,"w+")
        f.write(data_to_write)
        f.close()
        writer.writerow([data["publishAt"]["$date"][:10]])
        writer1.writerow([data["url"]])
        writer2.writerow([data["_id"]["$oid"]])
        count += 1
        if(count%100 == 0):
            print(str(count)+ " files generated..")
        # if(count%8000==0):
        #     break
    
    #close input file
    json_f.close()
    date_inp.close()
    print("All files created successfully!!!!!!")

if __name__ == "__main__":
    # needs 2 argument from command line
    # 1.input_path contains json data
    # 2.output_path is folder that will contain all the ouput files 
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    date_file = sys.argv[3]
    url_file = sys.argv[4]
    news_id = sys.argv[5]
    parseJson(input_path,output_path, date_file,url_file,news_id)
   
