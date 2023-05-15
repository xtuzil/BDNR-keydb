import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { RoomsComponent } from './rooms/rooms.component';
import { RoomPreviewComponent } from './rooms/room-preview/room-preview.component';
import { MessageComponent } from './chat/message/message.component';
import { ChatComponent } from './chat/chat.component';
import { ChatMessagesComponent } from './chat/chat-messages/chat-messages.component';

@NgModule({
  declarations: [
    AppComponent,
    RoomsComponent,
    RoomPreviewComponent,
    MessageComponent,
    ChatComponent,
    ChatMessagesComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
