# LabaNotator Shape Library Inspector

LabaNotator is a Labanotation document editor software, available for Windows. Shape libraries shown on the right pane, are saved as *.lib files in the folder such as "C:\Program Files (x86)\Kepha\LabaNotator\Libraries".

This script can edit these *.lib files directly. It implements the following features:

## Features

- Shape Library Inspector (ShapeLibraryInspector.pyw)
  - shape tree inspection
  - direct property edit
  - multilingual property edit (if the properties are defined as i18n text)
- Shape Library Editor (ShapeLibraryEditor.pyw)
  - change shape list order
  - copy shapes from other shape library file

Warning: *editing with the inspector might be unsafe* (it may occur some unfamiliar error messages, or unstable behaviors of the application).

Some properties are marked as "reserved"; those functionalities are unknown.

## Limitations

- ShapeLibraryEntry.I18nName does not display in LabaNotator.
- ShapeLibraryEntry.Comments should be an array of string, but this script supports a string, as the array that its number of elements are 1 at most.
- TMyImage bitmap edition is not supported.

## Requirements

- Python 3.x (Python 2.x is not supported)
- Windows (XP, 7 or later should be supported)

## license

MIT License
