# Incremental Downloader
Download PDF's served with incremental manner, by just providing single link.

# How to use
For example, on server there are files named

www.example.com/file1.pdf  
www.example.com/file2.pdf  
...  
www.example.com/fileN.pdf  

```
incremental-dl www.example.com/file +1 -N .pdf
```

This command download all files from 1 to N with pdf extension
