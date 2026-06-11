declare const wx: any;

export function persistBase64Image(base64: string, filename: string): Promise<string> {
  return new Promise((resolve, reject) => {
    // #ifdef MP-WEIXIN
    const safeName = filename || `ray-vision-${Date.now()}.png`;
    const filePath = `${wx.env.USER_DATA_PATH}/${safeName}`;
    wx.getFileSystemManager().writeFile({
      filePath,
      data: base64,
      encoding: "base64",
      success: () => resolve(filePath),
      fail: (error: { errMsg?: string }) => {
        reject(new Error(error.errMsg || "写入重建图像失败"));
      },
    });
    // #endif

    // #ifndef MP-WEIXIN
    resolve(`data:image/png;base64,${base64}`);
    // #endif
  });
}

export function saveImageToAlbum(filePath: string): Promise<void> {
  return new Promise((resolve, reject) => {
    uni.saveImageToPhotosAlbum({
      filePath,
      success: () => resolve(),
      fail: (error) => reject(new Error(error.errMsg || "保存图片失败")),
    });
  });
}
