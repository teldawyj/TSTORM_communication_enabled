//#define TINYTIFF_WRITE_COMMENTS
#define DLLEXPORT extern "C" __declspec(dllexport)

#include <math.h>
#include <float.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
//#include "tinytiffwriter_dll.h"

#ifndef __WINDOWS__
# if defined(WIN32) || defined(WIN64) || defined(_MSC_VER) || defined(_WIN32)
#  define __WINDOWS__
# endif
#endif

#ifndef __LINUX__
# if defined(linux)
#  define __LINUX__
# endif
#endif

#define __USE_LIBC_FOR_TIFF__
#ifdef __WINDOWS__
#  ifndef __USE_LIBC_FOR_TIFF__
#    define __USE_WINAPI_FOR_TIFF__
#  endif
#endif // __WINDOWS__

#ifdef __USE_WINAPI_FOR_TIFF__
#  include <windows.h>
#  warning COMPILING TinyTIFFWriter with WinAPI
#endif // __USE_WINAPI_FOR_TIFF__

#define TIFF_ORDER_UNKNOWN 0
#define TIFF_ORDER_BIGENDIAN 1
#define TIFF_ORDER_LITTLEENDIAN 2
#define TRUE (0==0)
#define FALSE (0==1)

#define TINYTIFFWRITER_DESCRIPTION_SIZE 1024

int TinyTIFFWriter_getMaxDescriptionTextSize() {
    return TINYTIFFWRITER_DESCRIPTION_SIZE;
}


int TIFF_get_byteorder()
{
        union {
                long l;
                char c[4];
        } test;
        test.l = 1;
        if( test.c[3] && !test.c[2] && !test.c[1] && !test.c[0] )
                return TIFF_ORDER_BIGENDIAN;

        if( !test.c[3] && !test.c[2] && !test.c[1] && test.c[0] )
                return TIFF_ORDER_LITTLEENDIAN;

        return TIFF_ORDER_UNKNOWN;
}



struct TinyTIFFFile {
#ifdef __USE_WINAPI_FOR_TIFF__
    
    HANDLE hFile;
#else
  
    FILE* file;
#endif // __USE_WINAPI_FOR_TIFF__
   
    uint32_t lastIFDOffsetField;
   
    long int lastStartPos;
   
    uint32_t lastIFDDATAAdress;
    
    uint16_t lastIFDCount;
   
    uint8_t* lastHeader;
    int lastHeaderSize;
  
    uint32_t pos;
   
    uint32_t width;
  
    uint32_t height;
  
    uint16_t bitspersample;
    uint32_t descriptionOffset;
    uint32_t descriptionSizeOffset;
   
    uint64_t frames;
    
    uint8_t byteorder;
};


inline void TinyTIFFWriter_fopen(TinyTIFFFile* tiff, const char* filename) {
#ifdef __USE_WINAPI_FOR_TIFF__
    tiff->hFile = CreateFile(filename,               // name of the write
                       GENERIC_WRITE,          // open for writing
                       0,                      // do not share
                       NULL,                   // default security
                       CREATE_NEW,             // create new file only
                       FILE_ATTRIBUTE_NORMAL|FILE_FLAG_WRITE_THROUGH,  // normal file
                       NULL);                  // no attr. template
#else
    tiff->file=fopen(filename, "wb");
#endif
}


inline int TinyTIFFWriter_fOK(TinyTIFFFile* tiff) {
#ifdef __USE_WINAPI_FOR_TIFF__
   if (tiff->hFile == INVALID_HANDLE_VALUE) return FALSE;
   else return TRUE;
#else
   if (tiff->file) return TRUE;
   else return FALSE;
#endif
}


inline int TinyTIFFWriter_fclose(TinyTIFFFile* tiff) {
#ifdef __USE_WINAPI_FOR_TIFF__
    CloseHandle(tiff->hFile);
    return 0;
#else
    int r=fclose(tiff->file);
    tiff->file=NULL;
    return r;
#endif
}


inline size_t TinyTIFFWriter_fwrite(void * ptr, size_t size, size_t count, TinyTIFFFile* tiff) {
#ifdef __USE_WINAPI_FOR_TIFF__
   DWORD dwBytesWritten = 0;
    WriteFile(
                    tiff->hFile,           // open file handle
                    ptr,      // start of data to write
                    size*count,  // number of bytes to write
                    &dwBytesWritten, // number of bytes that were written
                    NULL);
    return dwBytesWritten;
#else
    return fwrite(ptr, size, count, tiff->file);
#endif
}


inline long int TinyTIFFWriter_ftell ( TinyTIFFFile * tiff ) {
#ifdef __USE_WINAPI_FOR_TIFF__
DWORD dwPtr = SetFilePointer( tiff->hFile,
                                0,
                                NULL,
                                FILE_CURRENT );
    return dwPtr;
#else
    return ftell(tiff->file);
#endif
}



inline int TinyTIFFWriter_fseek_set(TinyTIFFFile* tiff, size_t offset) {
#ifdef __USE_WINAPI_FOR_TIFF__
   DWORD res = SetFilePointer (tiff->hFile,
                                offset,
                                NULL,
                                FILE_BEGIN);


   return res;
#else
    return fseek(tiff->file, offset, SEEK_SET);
#endif // __USE_WINAPI_FOR_TIFF__
}


inline int TinyTIFFWriter_fseek_cur(TinyTIFFFile* tiff, size_t offset) {
#ifdef __USE_WINAPI_FOR_TIFF__
   DWORD res = SetFilePointer (tiff->hFile,
                                offset,
                                NULL,
                                FILE_CURRENT);


   return res;
#else
    return fseek(tiff->file, offset, SEEK_CUR);
#endif // __USE_WINAPI_FOR_TIFF__
}

#define TIFF_FIELD_IMAGEWIDTH 256
#define TIFF_FIELD_IMAGELENGTH 257
#define TIFF_FIELD_BITSPERSAMPLE 258
#define TIFF_FIELD_COMPRESSION 259
#define TIFF_FIELD_PHOTOMETRICINTERPRETATION 262
#define TIFF_FIELD_IMAGEDESCRIPTION 270
#define TIFF_FIELD_STRIPOFFSETS 273
#define TIFF_FIELD_SAMPLESPERPIXEL 277
#define TIFF_FIELD_ROWSPERSTRIP 278
#define TIFF_FIELD_STRIPBYTECOUNTS 279
#define TIFF_FIELD_XRESOLUTION 282
#define TIFF_FIELD_YRESOLUTION 283
#define TIFF_FIELD_PLANARCONFIG 284
#define TIFF_FIELD_RESOLUTIONUNIT 296
#define TIFF_FIELD_SAMPLEFORMAT 339

#define TIFF_TYPE_BYTE 1
#define TIFF_TYPE_ASCII 2
#define TIFF_TYPE_SHORT 3
#define TIFF_TYPE_LONG 4
#define TIFF_TYPE_RATIONAL 5



#define TIFF_HEADER_SIZE 510

#define TIFF_HEADER_MAX_ENTRIES 16


#define WRITE32DIRECT(filen, data)  { \
    TinyTIFFWriter_fwrite((void*)(&(data)), 4, 1, filen); \
}


#define WRITE32DIRECT_CAST(filen, data)  { \
    uint32_t d=data; \
    WRITE32DIRECT((filen), d); \
}

#define WRITE16DIRECT(filen, data)    { \
    TinyTIFFWriter_fwrite((void*)(&(data)), 2, 1, filen); \
}


#define WRITE16DIRECT_CAST(filen, data)    { \
    uint16_t d=data; \
    WRITE16DIRECT((filen), d); \
}





#define WRITE8DIRECT(filen, data) {\
    uint8_t ch=data; \
    TinyTIFFWriter_fwrite(&ch, 1, 1, filen);\
}















#define WRITEH32DIRECT_LE(filen, data)  { \
    *((uint32_t*)(&filen->lastHeader[filen->pos]))=data; \
    filen->pos+=4;\
}

#define WRITEH32_LE(filen, data)  { \
    uint32_t d=data; \
    WRITEH32DIRECT_LE(filen, d); \
}

// write 2-bytes in big endian

#define WRITEH16DIRECT_LE(filen, data)    { \
    *((uint16_t*)(&filen->lastHeader[filen->pos]))=data; \
    filen->pos+=2; \
}


#define WRITEH16_LE(filen, data)    { \
    uint16_t d=data; \
    WRITEH16DIRECT_LE(filen, d); \
}


// write byte

#define WRITEH8(filen, data) { filen->lastHeader[filen->pos]=data; filen->pos+=1; }

#define WRITEH8DIRECT(filen, data) { filen->lastHeader[filen->pos]=data; filen->pos+=1; }

// write 2 bytes
#define WRITEH16(filen, data)  WRITEH16_LE(filen, data)
#define WRITEH32(filen, data)  WRITEH32_LE(filen, data)

#define WRITEH16DIRECT(filen, data)  WRITEH16DIRECT_LE(filen, data)
#define WRITEH32DIRECT(filen, data)  WRITEH32DIRECT_LE(filen, data)


inline void TinyTIFFWriter_startIFD(TinyTIFFFile* tiff, int hsize=TIFF_HEADER_SIZE) {
    if (!tiff) return;
    tiff->lastStartPos=TinyTIFFWriter_ftell(tiff);//ftell(tiff->file);
    //tiff->lastIFDEndAdress=startPos+2+TIFF_HEADER_SIZE;
    tiff->lastIFDDATAAdress=2+TIFF_HEADER_MAX_ENTRIES*12;
    tiff->lastIFDCount=0;
    if (tiff->lastHeader && hsize!=tiff->lastHeaderSize) {
        free(tiff->lastHeader);
        tiff->lastHeader=NULL;
        tiff->lastHeaderSize=0;
    }
    if (!tiff->lastHeader) {
        tiff->lastHeader=(uint8_t*)calloc(hsize+2, 1);
        tiff->lastHeaderSize=hsize;
    } else {
        memset(tiff->lastHeader, 0, hsize+2);
    }
    tiff->pos=2;
}


inline void TinyTIFFWriter_endIFD(TinyTIFFFile* tiff, int hsize=TIFF_HEADER_SIZE) {
    if (!tiff) return;
    //long startPos=ftell(tiff->file);

    tiff->pos=0;
    WRITEH16DIRECT(tiff, tiff->lastIFDCount);

    tiff->pos=2+tiff->lastIFDCount*12; // header start (2byte) + 12 bytes per IFD entry
    WRITEH32(tiff, tiff->lastStartPos+2+hsize+tiff->width*tiff->height*(tiff->bitspersample/8));
    //printf("imagesize = %d\n", tiff->width*tiff->height*(tiff->bitspersample/8));

    //fwrite((void*)tiff->lastHeader, TIFF_HEADER_SIZE+2, 1, tiff->file);
    TinyTIFFWriter_fwrite((void*)tiff->lastHeader, tiff->lastHeaderSize+2, 1, tiff);
    tiff->lastIFDOffsetField=tiff->lastStartPos+2+tiff->lastIFDCount*12;
    //free(tiff->lastHeader);
    //tiff->lastHeader=NULL;
}


inline void TinyTIFFWriter_writeIFDEntry(TinyTIFFFile* tiff, uint16_t tag, uint16_t type, uint32_t count, uint32_t data) {
    if (!tiff) return;
    if (tiff->lastIFDCount<TIFF_HEADER_MAX_ENTRIES) {
        tiff->lastIFDCount++;
        WRITEH16DIRECT(tiff, tag);
        WRITEH16DIRECT(tiff, type);
        WRITEH32DIRECT(tiff, count);
        WRITEH32DIRECT(tiff, data);
    }
}


 inline void TinyTIFFWriter_writeIFDEntryBYTE(TinyTIFFFile* tiff, uint16_t tag, uint8_t data) {
    if (!tiff) return;
    if (tiff->lastIFDCount<TIFF_HEADER_MAX_ENTRIES) {
        tiff->lastIFDCount++;
        WRITEH16DIRECT(tiff, tag);
        WRITEH16(tiff, TIFF_TYPE_BYTE);
        WRITEH32(tiff, 1);
        WRITEH8DIRECT(tiff, data);
        WRITEH8(tiff, 0);
        WRITEH16(tiff, 0);
    }
}


 void TinyTIFFWriter_writeIFDEntrySHORT(TinyTIFFFile* tiff, uint16_t tag, uint16_t data) {
    if (!tiff) return;
    if (tiff->lastIFDCount<TIFF_HEADER_MAX_ENTRIES) {
        tiff->lastIFDCount++;
        WRITEH16DIRECT(tiff, tag);
        WRITEH16(tiff, TIFF_TYPE_SHORT);
        WRITEH32(tiff, 1);
        WRITEH16DIRECT(tiff, data);
        WRITEH16(tiff, 0);
    }
}


 inline void TinyTIFFWriter_writeIFDEntryLONG(TinyTIFFFile* tiff, uint16_t tag, uint32_t data) {
    if (!tiff) return;
    if (tiff->lastIFDCount<TIFF_HEADER_MAX_ENTRIES) {
        tiff->lastIFDCount++;
        WRITEH16DIRECT(tiff, tag);
        WRITEH16(tiff, TIFF_TYPE_LONG);
        WRITEH32(tiff, 1);
        WRITEH32DIRECT(tiff, data);
    }
}


 inline void TinyTIFFWriter_writeIFDEntryLONGARRAY(TinyTIFFFile* tiff, uint16_t tag, uint32_t* data, uint32_t N) {
    if (!tiff) return;
    if (tiff->lastIFDCount<TIFF_HEADER_MAX_ENTRIES) {
        tiff->lastIFDCount++;
        WRITEH16DIRECT(tiff, tag);
        WRITEH16(tiff, TIFF_TYPE_LONG);
        WRITEH32(tiff, N);
        if (N==1) {
            WRITEH32DIRECT(tiff, *data);
        } else {
            WRITEH32DIRECT(tiff, tiff->lastIFDDATAAdress+tiff->lastStartPos);
            int pos=tiff->pos;
            tiff->pos=tiff->lastIFDDATAAdress;
            for (uint32_t i=0; i<N; i++) {
                WRITEH32DIRECT(tiff, data[i]);
            }
            tiff->lastIFDDATAAdress=tiff->pos;
            tiff->pos=pos;
        }
    }
}


inline void TinyTIFFWriter_writeIFDEntrySHORTARRAY(TinyTIFFFile* tiff, uint16_t tag, uint16_t* data, uint32_t N) {
    if (!tiff) return;
    if (tiff->lastIFDCount<TIFF_HEADER_MAX_ENTRIES) {
        tiff->lastIFDCount++;
        WRITEH16DIRECT(tiff, tag);
        WRITEH16(tiff, TIFF_TYPE_SHORT);
        WRITEH32(tiff, N);
        if (N==1) {
            WRITEH32DIRECT(tiff, *data);
        } else {
            WRITEH32DIRECT(tiff, tiff->lastIFDDATAAdress+tiff->lastStartPos);
            int pos=tiff->pos;
            tiff->pos=tiff->lastIFDDATAAdress;
            for (uint32_t i=0; i<N; i++) {
                WRITEH16DIRECT(tiff, data[i]);
            }
            tiff->lastIFDDATAAdress=tiff->pos;
            tiff->pos=pos;
        }


    }
}


inline void TinyTIFFWriter_writeIFDEntryASCIIARRAY(TinyTIFFFile* tiff, uint16_t tag, char* data, uint32_t N, int* datapos=NULL, int* sizepos=NULL) {
    if (!tiff) return;
    if (tiff->lastIFDCount<TIFF_HEADER_MAX_ENTRIES) {
        tiff->lastIFDCount++;
        WRITEH16DIRECT(tiff, tag);
        WRITEH16(tiff, TIFF_TYPE_ASCII);
        if (sizepos) *sizepos=tiff->pos;
        WRITEH32(tiff, N);
        if (N<4) {
            if (datapos) *datapos=tiff->pos;
            for (uint32_t i=0; i<4; i++) {
                if (i<N) {
                    WRITEH8DIRECT(tiff, data[i]);
                } else {
                    WRITEH8DIRECT(tiff, 0);
                }
            }
        } else {
            WRITEH32DIRECT(tiff, tiff->lastIFDDATAAdress+tiff->lastStartPos);
            int pos=tiff->pos;
            tiff->pos=tiff->lastIFDDATAAdress;
            if (datapos) *datapos=tiff->pos;
            for (uint32_t i=0; i<N; i++) {
                WRITEH8DIRECT(tiff, data[i]);
            }
            tiff->lastIFDDATAAdress=tiff->pos;
            tiff->pos=pos;
        }


    }
}


inline void TinyTIFFWriter_writeIFDEntryRATIONAL(TinyTIFFFile* tiff, uint16_t tag, uint32_t numerator, uint32_t denominator) {
    if (!tiff) return;
    if (tiff->lastIFDCount<TIFF_HEADER_MAX_ENTRIES) {
        tiff->lastIFDCount++;
        WRITEH16DIRECT(tiff, tag);
        WRITEH16(tiff, TIFF_TYPE_RATIONAL);
        WRITEH32(tiff, 1);
        WRITEH32DIRECT(tiff, tiff->lastIFDDATAAdress+tiff->lastStartPos);
        //printf("1 - %lx\n", tiff->pos);
        int pos=tiff->pos;
        tiff->pos=tiff->lastIFDDATAAdress;
        //printf("2 - %lx\n", tiff->pos);
        WRITEH32DIRECT(tiff, numerator);
        //printf("3 - %lx\n", tiff->pos);
        WRITEH32DIRECT(tiff, denominator);
        tiff->lastIFDDATAAdress=tiff->pos;
        tiff->pos=pos;
        //printf("4 - %lx\n", tiff->pos);
    }
}



DLLEXPORT TinyTIFFFile* TinyTIFFWriter_open(const char* filename, uint16_t bitsPerSample, uint32_t width, uint32_t height) {
    TinyTIFFFile* tiff=(TinyTIFFFile*)malloc(sizeof(TinyTIFFFile));

    //tiff->file=fopen(filename, "wb");
    TinyTIFFWriter_fopen(tiff, filename);
    tiff->width=width;
    tiff->height=height;
    tiff->bitspersample=bitsPerSample;
    tiff->lastHeader=NULL;
    tiff->lastHeaderSize=0;
    tiff->byteorder=TIFF_get_byteorder();
    tiff->frames=0;

    if (TinyTIFFWriter_fOK(tiff)) {
        if (TIFF_get_byteorder()==TIFF_ORDER_BIGENDIAN) {
            WRITE8DIRECT(tiff, 'M');   // write TIFF header for big-endian
            WRITE8DIRECT(tiff, 'M');
        } else {
            WRITE8DIRECT(tiff, 'I');   // write TIFF header for little-endian
            WRITE8DIRECT(tiff, 'I');
        }
        WRITE16DIRECT_CAST(tiff, 42);
        tiff->lastIFDOffsetField=TinyTIFFWriter_ftell(tiff);//ftell(tiff->file);
        WRITE32DIRECT_CAST(tiff, 8);      // now write offset to first IFD, which is simply 8 here (in little-endian order)
        return tiff;
    } else {
        free(tiff);
        return NULL;
    }
}
#ifdef TINYTIFF_WRITE_COMMENTS
void TinyTIFFWriter_close(TinyTIFFFile* tiff, char* imageDescription) {
#else
void TinyTIFFWriter_close(TinyTIFFFile* tiff, char* /*imageDescription*/) {
#endif
   if (tiff) {
        TinyTIFFWriter_fseek_set(tiff, tiff->lastIFDOffsetField);
        WRITE32DIRECT_CAST(tiff, 0);
#ifdef TINYTIFF_WRITE_COMMENTS
        if (tiff->descriptionOffset>0) {
          size_t dlen;
          char description[TINYTIFFWRITER_DESCRIPTION_SIZE+1];

          if (imageDescription) {
              strcpy(description, imageDescription);
          } else {
		      for (int i=0; i<TINYTIFFWRITER_DESCRIPTION_SIZE+1; i++) description[i]='\0';
              sprintf(description, "TinyTIFFWriter_version=1.1\nimages=%ld", tiff->frames);
		  }
          description[TINYTIFFWRITER_DESCRIPTION_SIZE-1]='\0';
          dlen=strlen(description);
          printf("WRITING COMMENT\n***");
          printf(description);
          printf("***\nlen=%ld\n\n", dlen);
          TinyTIFFWriter_fseek_set(tiff, tiff->descriptionOffset);
          TinyTIFFWriter_fwrite(description, 1, dlen+1, tiff);//<<" / "<<dlen<<"\n";
          TinyTIFFWriter_fseek_set(tiff, tiff->descriptionSizeOffset);
          WRITE32DIRECT_CAST(tiff, (dlen+1));
        }
#endif // TINYTIFF_WRITE_COMMENTS
        TinyTIFFWriter_fclose(tiff);
        free(tiff->lastHeader);
        free(tiff);
    }
}

DLLEXPORT void TinyTIFFWriter_close(TinyTIFFFile* tiff, double pixel_width, double pixel_height, double frametime, double deltaz) {
    if (tiff) {
      char description[TINYTIFFWRITER_DESCRIPTION_SIZE+1];
	  for (int i=0; i<TINYTIFFWRITER_DESCRIPTION_SIZE+1; i++) description[i]='\0';
      char spw[256];
      sprintf(description, "TinyTIFFWriter_version=1.1\nimages=%lu", (unsigned long int)tiff->frames);
      if (fabs(pixel_width)>10.0*DBL_MIN) {
          sprintf(spw, "\npixel_width=%lf ", pixel_width);
          strcat(description, spw);
      }
      if (fabs(pixel_height)>10.0*DBL_MIN) {
          sprintf(spw, "\npixel_height=%lf ", pixel_height);
          strcat(description,spw);
      }
      if (fabs(deltaz)>10.0*DBL_MIN) {
          sprintf(spw, "\ndeltaz=%lf ", deltaz);
          strcat(description,spw);
      }
      if (fabs(frametime)>10.0*DBL_MIN) {
          sprintf(spw, "\nframetime=%lg ", frametime);
          strcat(description,spw);
      }
      description[TINYTIFFWRITER_DESCRIPTION_SIZE-1]='\0';
      TinyTIFFWriter_close(tiff, description);
    }
}

#define TINTIFFWRITER_WRITEImageDescriptionTemplate(tiff) \
    if (tiff->frames<=0) {\
        int datapos=0;\
        int sizepos=0;\
        char description[TINYTIFFWRITER_DESCRIPTION_SIZE+1];\
        for (int i=0; i<TINYTIFFWRITER_DESCRIPTION_SIZE+1; i++) description[i]='\0';\
        sprintf(description, "TinyTIFFWriter_version=1.1\n");\
        description[TINYTIFFWRITER_DESCRIPTION_SIZE]='\0';\
        TinyTIFFWriter_writeIFDEntryASCIIARRAY(tiff, TIFF_FIELD_IMAGEDESCRIPTION, description, TINYTIFFWRITER_DESCRIPTION_SIZE, &datapos, &sizepos);\
        tiff->descriptionOffset=tiff->lastStartPos+datapos;\
        tiff->descriptionSizeOffset=tiff->lastStartPos+sizepos;\
     }


DLLEXPORT void TinyTIFFWriter_writeImage_void(TinyTIFFFile* tiff, void* data) {
     if (!tiff) return;
     long pos=TinyTIFFWriter_ftell(tiff);
     int hsize=TIFF_HEADER_SIZE;
#ifdef TINYTIFF_WRITE_COMMENTS
     if (tiff->frames<=0) {
        hsize=TIFF_HEADER_SIZE+TINYTIFFWRITER_DESCRIPTION_SIZE+16;
      }
#endif // TINYTIFF_WRITE_COMMENTS
    TinyTIFFWriter_startIFD(tiff,hsize);
    TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_IMAGEWIDTH, tiff->width);
    TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_IMAGELENGTH, tiff->height);
    TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_BITSPERSAMPLE, tiff->bitspersample);
    TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_COMPRESSION, 1);
    TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_PHOTOMETRICINTERPRETATION, 1);
#ifdef TINYTIFF_WRITE_COMMENTS
    TINTIFFWRITER_WRITEImageDescriptionTemplate(tiff);
#endif // TINYTIFF_WRITE_COMMENTS
    TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_STRIPOFFSETS, pos+2+hsize);
    TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_SAMPLESPERPIXEL, 1);
    TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_ROWSPERSTRIP, tiff->height);
    TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_STRIPBYTECOUNTS, tiff->width*tiff->height*(tiff->bitspersample/8));
    TinyTIFFWriter_writeIFDEntryRATIONAL(tiff, TIFF_FIELD_XRESOLUTION, 1,1);
    TinyTIFFWriter_writeIFDEntryRATIONAL(tiff, TIFF_FIELD_YRESOLUTION, 1,1);
    TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_PLANARCONFIG, 1);
    TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_RESOLUTIONUNIT, 1);
    TinyTIFFWriter_endIFD(tiff);
    TinyTIFFWriter_fwrite(data, tiff->width*tiff->height*(tiff->bitspersample/8), 1, tiff);
    tiff->frames=tiff->frames+1;
}



DLLEXPORT void TinyTIFFWriter_writeImage_float(TinyTIFFFile* tiff, float* data) {
     if (!tiff) return;
     long pos=ftell(tiff->file);
     int hsize=TIFF_HEADER_SIZE;
#ifdef TINYTIFF_WRITE_COMMENTS
     if (tiff->frames<=0) {
        hsize=TIFF_HEADER_SIZE+TINYTIFFWRITER_DESCRIPTION_SIZE+16;
      }
#endif // TINYTIFF_WRITE_COMMENTS

     TinyTIFFWriter_startIFD(tiff,hsize);
     TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_IMAGEWIDTH, tiff->width);
     TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_IMAGELENGTH, tiff->height);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_BITSPERSAMPLE, tiff->bitspersample);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_COMPRESSION, 1);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_PHOTOMETRICINTERPRETATION, 1);
#ifdef TINYTIFF_WRITE_COMMENTS
    TINTIFFWRITER_WRITEImageDescriptionTemplate(tiff);
#endif // TINYTIFF_WRITE_COMMENTS
     TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_STRIPOFFSETS, pos+2+hsize);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_SAMPLESPERPIXEL, 1);
     TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_ROWSPERSTRIP, tiff->height);
     TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_STRIPBYTECOUNTS, tiff->width*tiff->height*(tiff->bitspersample/8));
     TinyTIFFWriter_writeIFDEntryRATIONAL(tiff, TIFF_FIELD_XRESOLUTION, 1,1);
     TinyTIFFWriter_writeIFDEntryRATIONAL(tiff, TIFF_FIELD_YRESOLUTION, 1,1);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_PLANARCONFIG, 1);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_RESOLUTIONUNIT, 1);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_SAMPLEFORMAT, 3);
     TinyTIFFWriter_endIFD(tiff);
     TinyTIFFWriter_fwrite(data, tiff->width*tiff->height*(tiff->bitspersample/8), 1, tiff);
     tiff->frames=tiff->frames+1;
}







DLLEXPORT void TinyTIFFWriter_writeImage_double(TinyTIFFFile* tiff, double* data) {
     if (!tiff) return;
     long pos=ftell(tiff->file);
     int hsize=TIFF_HEADER_SIZE;
#ifdef TINYTIFF_WRITE_COMMENTS
     if (tiff->frames<=0) {
        hsize=TIFF_HEADER_SIZE+TINYTIFFWRITER_DESCRIPTION_SIZE+16;
      }
#endif // TINYTIFF_WRITE_COMMENTS

     TinyTIFFWriter_startIFD(tiff,hsize);
     TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_IMAGEWIDTH, tiff->width);
     TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_IMAGELENGTH, tiff->height);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_BITSPERSAMPLE, tiff->bitspersample);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_COMPRESSION, 1);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_PHOTOMETRICINTERPRETATION, 1);
#ifdef TINYTIFF_WRITE_COMMENTS
    TINTIFFWRITER_WRITEImageDescriptionTemplate(tiff);
#endif // TINYTIFF_WRITE_COMMENTS
     TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_STRIPOFFSETS, pos+2+hsize);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_SAMPLESPERPIXEL, 1);
     TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_ROWSPERSTRIP, tiff->height);
     TinyTIFFWriter_writeIFDEntryLONG(tiff, TIFF_FIELD_STRIPBYTECOUNTS, tiff->width*tiff->height*(tiff->bitspersample/8));
     TinyTIFFWriter_writeIFDEntryRATIONAL(tiff, TIFF_FIELD_XRESOLUTION, 1,1);
     TinyTIFFWriter_writeIFDEntryRATIONAL(tiff, TIFF_FIELD_YRESOLUTION, 1,1);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_PLANARCONFIG, 1);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_RESOLUTIONUNIT, 1);
     TinyTIFFWriter_writeIFDEntrySHORT(tiff, TIFF_FIELD_SAMPLEFORMAT, 3);
     TinyTIFFWriter_endIFD(tiff);
     TinyTIFFWriter_fwrite(data, tiff->width*tiff->height*(tiff->bitspersample/8), 1, tiff);
     tiff->frames=tiff->frames+1;
}

DLLEXPORT int add(int a, int b){
     return a+b;
}