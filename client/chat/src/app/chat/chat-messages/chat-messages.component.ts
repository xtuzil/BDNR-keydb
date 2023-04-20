import { ChangeDetectorRef, Component, Input, OnInit } from '@angular/core';
import { AppService, Message } from 'src/app/app.service';

@Component({
  selector: 'app-chat-messages',
  templateUrl: './chat-messages.component.html',
  styleUrls: ['./chat-messages.component.scss'],
})
export class ChatMessagesComponent implements OnInit {
  @Input()
  messages: Message[] = [];

  constructor(private service: AppService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.service.message.subscribe((msg) => {
      this.messages = [msg, ...this.messages];
      this.cdr.detectChanges();
      console.log('NEW MESSAGES: ', this.messages);
    });
    this.service.getMessagesStream();
  }
}
